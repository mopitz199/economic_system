from decimal import Decimal
from typing import Optional, List, Dict, Any

from gekko import GEKKO

from django.contrib.auth.models import User
from django.db import transaction

from apps.asset.models import Asset
from apps.chart.constants import MILESTONE_CRISIS, MILESTONE_ABUNDANCE
from apps.chart.models import AssetMilestone, Milestone

from apps.portfolio_optimization.models import (
    AssetOptimization,
    PortfolioOptimization,
)


def create_or_update_asset_optimization(
    asset_id: int,
    min_to_invest: float,
    max_to_invest: float,
    portfolio_optimization_id: int,
    amount_to_invest: Optional[Decimal] = None,
    id: Optional[int] = None,
) -> AssetOptimization:
    portfolio_optimization = PortfolioOptimization.objects.get(
        id=portfolio_optimization_id
    )
    asset = Asset.objects.get(id=asset_id)

    if id:
        asset_optimization = AssetOptimization.objects.get(id=id)
    else:
        asset_optimization = AssetOptimization()

    asset_optimization.asset = asset
    asset_optimization.portfolio_optimization = portfolio_optimization
    asset_optimization.min_to_invest = min_to_invest
    asset_optimization.max_to_invest = max_to_invest
    asset_optimization.amount_to_invest = amount_to_invest
    asset_optimization.save()
    return asset_optimization


def create_empty_portoflio_optimization(user: User) -> PortfolioOptimization:
    from apps.portfolio_optimization.api_serializers import (
        RequestCreatePortfolioOptimizationSerializer
    )

    data = {
        "name": "My first optimization",
        "user": user.id,
        "min_disposed_to_lose": 100,
        "optimism": 50,
        "asset_optimizations": []
    }
    serializer = RequestCreatePortfolioOptimizationSerializer(data=data)
    assert serializer.is_valid()
    portfolio_optimization = create_or_update_portfolio_optimization(
        serializer
    )
    return portfolio_optimization


@transaction.atomic
def create_or_update_portfolio_optimization(
    serializer: "RequestCreatePortfolioOptimizationSerializer"
) -> PortfolioOptimization:
    data = serializer.validated_data

    portfolio_optimization_id = data.get('id')
    if portfolio_optimization_id:
        portfolio_optimization = PortfolioOptimization.objects.get(
            id=portfolio_optimization_id
        )
    else:
        portfolio_optimization = PortfolioOptimization()

    user = User.objects.get(id=data['user'])

    portfolio_optimization.name = data['name']
    portfolio_optimization.user = user
    portfolio_optimization.min_disposed_to_lose = data['min_disposed_to_lose']
    portfolio_optimization.total_amount_to_invest = data.get(
        'total_amount_to_invest'
    )
    portfolio_optimization.optimism = data['optimism']
    portfolio_optimization.save()

    asset_optimization_ids = []
    for asset_optimization_data in data['asset_optimizations']:
        asset_optimization = create_or_update_asset_optimization(
            id=asset_optimization_data.get('id'),
            asset_id=asset_optimization_data['asset'].id,
            min_to_invest=asset_optimization_data['min_to_invest'],
            max_to_invest=asset_optimization_data['max_to_invest'],
            amount_to_invest=asset_optimization_data.get('amount_to_invest'),
            portfolio_optimization_id=portfolio_optimization.id
        )
        asset_optimization_ids.append(asset_optimization.id)
    portfolio_optimization.assetoptimization_set.exclude(
        id__in=asset_optimization_ids
    ).delete()
    return portfolio_optimization


def set_milestone_model_restrictions(
    asset_milestones: List[AssetMilestone],
    variables: Dict,
    model: GEKKO,
    min_to_lose: Decimal
):
    """Get the restrictions of the model according to the milestone
    and the given assets"""

    equation = None
    for asset_milestone in asset_milestones:
        if asset_milestone.deepest_down is not None:
            percentage_rate = 1+(asset_milestone.deepest_down/float(100))
            if equation is None:
                equation = (
                    variables[asset_milestone.asset_id]*percentage_rate
                )
            else:
                equation += (
                    variables[asset_milestone.asset_id]*percentage_rate
                )
    if equation is not None:
        return model.Equation(equation > min_to_lose)
    else:
        return None


def set_asset_optimization_restrictions(
    model: GEKKO,
    variable: Any,
    total_amount_to_invest: Decimal,
    min_percentage_to_invest: Optional[float],
    max_percentage_to_invest: Optional[float],
    amount_to_invest: Optional[Decimal] = None,
):
    """Set all the quation restriction of an asset optimization data"""

    equation1 = None
    if min_percentage_to_invest is not None:
        min_percentage_to_invest = min_percentage_to_invest/float(100)
        equation1 = model.Equation(
            variable >= float(total_amount_to_invest)*min_percentage_to_invest
        )

    equation2 = None
    if max_percentage_to_invest is not None:
        max_percentage_to_invest = max_percentage_to_invest/float(100)
        equation2 = model.Equation(
            variable <= float(total_amount_to_invest)*max_percentage_to_invest
        )

    equation3 = None
    if amount_to_invest is not None:
        equation3 = model.Equation(variable == amount_to_invest)

    equation4 = model.Equation(variable >= 0)

    return {
        'min_percentage_to_invest': equation1,
        'max_percentage_to_invest': equation2,
        'amount_to_invest': equation3,
        'no_zero': equation4
    }


def set_total_amount_to_invest_restriction(
    model: GEKKO,
    total_amount_to_invest: Decimal,
    variables: Dict,
):
    """Get the restricton of the total amount to invest"""
    equation = 0
    for key in variables:
        equation += variables[key]
    return model.Equation(equation == total_amount_to_invest)


def set_model_variables(model: GEKKO, asset_optimizations_data):
    variables = {}
    for asset_optimization_data in asset_optimizations_data:
        variables[asset_optimization_data['asset_id']] = model.Var()
    return variables


def get_total_performance_abundance_average(asset: Asset) -> Optional[float]:
    """Get the average of the total performance in the
    abundance period of all asset milestones"""

    asset_milestones = AssetMilestone.objects.filter(
        asset=asset,
        milestone__milestone_type=MILESTONE_ABUNDANCE,
    ).exclude(milestone__end=None)

    average = None
    index = 0
    for asset_milestone in asset_milestones:
        if asset_milestone.total_performance is not None:
            if average is None:
                average = 0
            index += 1
            average += asset_milestone.total_performance
    if average is not None:
        return average/float(index)
    else:
        return average


def get_total_performance_crisis_average(asset: Asset) -> Optional[float]:
    """Get the average of the total performance in the
    abundance period of all asset milestones"""

    asset_milestones = AssetMilestone.objects.filter(
        asset=asset,
        milestone__milestone_type=MILESTONE_CRISIS,
    ).exclude(milestone__end=None)

    average = None
    index = 0
    for asset_milestone in asset_milestones:
        if asset_milestone.total_performance is not None:
            if average is None:
                average = 0
            index += 1
            average += asset_milestone.total_performance
    if average is not None:
        return average/float(index)
    else:
        return average


def set_equation_to_optimize(
    model: GEKKO,
    variables: Dict,
    asset_optimizations_data: Dict,
    optimization_type: str,
):
    """Set the equation to optimaze"""

    equation = 0
    for asset_optimization_data in asset_optimizations_data:
        asset_id = asset_optimization_data['asset_id']
        variable = variables[asset_id]
        asset = Asset.objects.get(id=asset_id)
        if optimization_type == MILESTONE_ABUNDANCE:
            average = get_total_performance_abundance_average(asset)
        elif optimization_type == MILESTONE_CRISIS:
            average = get_total_performance_crisis_average(asset)
        else:
            raise Exception(f"The milestone type {optimization_type} doesn't exists")
        if average:
            equation += (variable*average)
    return model.Obj(-1*(equation))


def optimize_model(data: "RequestOptimizationSerializer"):
    optimism = data.validated_data.get('optimism', 50)
    pessimism = 100 - optimism

    optimism = optimism/float(100)
    pessimism = pessimism/float(100)

    crisis_response = build_optimization_model(data, 'crisis')
    abundance_response = build_optimization_model(data, 'abundance')

    amounts = {}
    for asset_id in crisis_response:
        crisis_value = crisis_response[asset_id]*pessimism
        abundance_value = abundance_response[asset_id]*optimism
        amounts[asset_id] = crisis_value + abundance_value

    total = 0
    for asset_id in amounts:
        total += amounts[asset_id]

    response = {}
    for asset_id in amounts:
        percentage = round(((amounts[asset_id]*100)/total), 2)
        response[asset_id] = {
            "percentage": percentage
        }
        if data.validated_data.get('total_amount_to_invest') is not None:
            response[asset_id]["amount"] = round(amounts[asset_id], 2)
    return response


def build_optimization_model(
    data: "RequestOptimizationSerializer",
    optimization_type: str,
):
    data = data.validated_data
    model = GEKKO(remote=False)

    total_amount_to_invest = data.get('total_amount_to_invest', 1000)
    variables = set_model_variables(model, data['asset_optimizations'])

    set_total_amount_to_invest_restriction(
        model,
        total_amount_to_invest,
        variables
    )

    asset_ids = []
    for asset_optimization_data in data['asset_optimizations']:
        asset_id = asset_optimization_data['asset_id']
        asset_ids.append(asset_id)

        amount_to_invest = asset_optimization_data.get('amount_to_invest')
        min_to_invest = asset_optimization_data.get('min_to_invest')
        max_to_invest = asset_optimization_data.get('max_to_invest')

        set_asset_optimization_restrictions(
            model=model,
            variable=variables[asset_id],
            total_amount_to_invest=total_amount_to_invest,
            min_percentage_to_invest=min_to_invest,
            max_percentage_to_invest=max_to_invest,
            amount_to_invest=amount_to_invest,
        )

    min_disposed_to_lose = data['min_disposed_to_lose']
    min_disposed_to_lose = 1-(min_disposed_to_lose/float(100))
    min_amount_disposed_to_lose = float(total_amount_to_invest)*min_disposed_to_lose

    for milestone in Milestone.objects.all():
        asset_milestones = AssetMilestone.objects.filter(
            asset_id__in=asset_ids,
            milestone=milestone
        )
        set_milestone_model_restrictions(
            asset_milestones=asset_milestones,
            variables=variables,
            model=model,
            min_to_lose=min_amount_disposed_to_lose
        )

    set_equation_to_optimize(
        model,
        variables,
        data['asset_optimizations'],
        optimization_type,
    )
    model.solve(disp=False)

    response = {}
    for key in variables:
        response[key] = variables[key].value[0]
    return response
