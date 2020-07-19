import pytest

from datetime import datetime, timedelta
from decimal import Decimal
from freezegun import freeze_time
from gekko import GEKKO
from model_bakery import baker
from unittest import mock

from apps.chart.constants import MILESTONE_ABUNDANCE, MILESTONE_CRISIS

from apps.portfolio_optimization.api_serializers import (
    RequestCreatePortfolioOptimizationSerializer,
)

from apps.portfolio_optimization.services import (
    create_or_update_asset_optimization,
    create_or_update_portfolio_optimization,
    set_milestone_model_restrictions,
    set_asset_optimization_restrictions,
    set_total_amount_to_invest_restriction,
    get_total_performance_abundance_average,
    get_total_performance_crisis_average,
)


@pytest.mark.django_db
def test_create_or_update_asset_optimization():
    asset = baker.make('Asset')
    portfolio_optimization = baker.make('PortfolioOptimization')
    asset_optimization = create_or_update_asset_optimization(
        asset_id=asset.id,
        min_to_invest=10.5,
        max_to_invest=40.2,
        portfolio_optimization_id=portfolio_optimization.id,
    )

    assert asset_optimization.asset_id == asset.id
    assert asset_optimization.portfolio_optimization_id == portfolio_optimization.id
    assert asset_optimization.min_to_invest == 10.5
    assert asset_optimization.max_to_invest == 40.2


@pytest.mark.django_db
def test_create_or_update_portfolio_optimization_create():
    asset = baker.make('Asset')
    user = baker.make('User')

    data = {
        "name": "My first optimization",
        "user": user.id,
        "min_disposed_to_lose": 80.3,
        "optimism": 50,
        "asset_optimizations": [
            {
                "asset": asset.id,
                "min_to_invest": 20,
                "max_to_invest": 40
            }
        ]
    }
    serializer = RequestCreatePortfolioOptimizationSerializer(data=data)
    assert serializer.is_valid()
    portfolio_optimization = create_or_update_portfolio_optimization(
        serializer
    )

    assert portfolio_optimization.name == data['name']
    assert portfolio_optimization.optimism == data['optimism']
    assert portfolio_optimization.user == user
    assert portfolio_optimization.min_disposed_to_lose == data.get(
        'min_disposed_to_lose'
    )
    assert portfolio_optimization.assetoptimization_set.all().count() == 1

    asset_optimization = portfolio_optimization.assetoptimization_set.last()
    assert asset_optimization.asset_id == data.get(
        'asset_optimizations'
    )[0]['asset']
    assert asset_optimization.min_to_invest == data.get(
        'asset_optimizations'
    )[0]['min_to_invest']
    assert asset_optimization.max_to_invest == data.get(
        'asset_optimizations'
    )[0]['max_to_invest']


@pytest.mark.django_db
def test_create_or_update_portfolio_optimization_update():
    asset = baker.make('Asset')
    user = baker.make('User')
    portfolio_optimization = baker.make('PortfolioOptimization')
    asset_optimization = baker.make(
        'AssetOptimization',
        portfolio_optimization=portfolio_optimization,
        asset=asset,
    )

    data = {
        "id": portfolio_optimization.id,
        "name": "My first optimization",
        "user": user.id,
        "optimism": 50,
        "min_disposed_to_lose": 80.3,
        "asset_optimizations": [
            {
                "id": asset_optimization.id,
                "asset": asset.id,
                "min_to_invest": 20,
                "max_to_invest": 40
            }
        ]
    }
    serializer = RequestCreatePortfolioOptimizationSerializer(data=data)
    assert serializer.is_valid()
    portfolio_optimization = create_or_update_portfolio_optimization(
        serializer
    )
    assert portfolio_optimization.id == data['id']
    assert portfolio_optimization.name == data['name']
    assert portfolio_optimization.optimism == data['optimism']
    assert portfolio_optimization.user == user
    assert portfolio_optimization.min_disposed_to_lose == data.get(
        'min_disposed_to_lose'
    )
    assert portfolio_optimization.assetoptimization_set.all().count() == 1

    asset_optimization = portfolio_optimization.assetoptimization_set.last()
    assert asset_optimization.id == data.get(
        'asset_optimizations'
    )[0]['id']
    assert asset_optimization.asset_id == data.get(
        'asset_optimizations'
    )[0]['asset']
    assert asset_optimization.min_to_invest == data.get(
        'asset_optimizations'
    )[0]['min_to_invest']
    assert asset_optimization.max_to_invest == data.get(
        'asset_optimizations'
    )[0]['max_to_invest']


@pytest.mark.django_db
def test_create_or_update_portfolio_optimization_update_delete():
    asset = baker.make('Asset')
    user = baker.make('User')
    portfolio_optimization = baker.make('PortfolioOptimization')
    baker.make(
        'AssetOptimization',
        portfolio_optimization=portfolio_optimization,
        asset=asset,
    )

    data = {
        "id": portfolio_optimization.id,
        "name": "My first optimization",
        "user": user.id,
        "optimism": 50,
        "min_disposed_to_lose": 80.3,
        "asset_optimizations": []
    }
    serializer = RequestCreatePortfolioOptimizationSerializer(data=data)
    assert serializer.is_valid()
    portfolio_optimization = create_or_update_portfolio_optimization(
        serializer
    )
    assert portfolio_optimization.id == data['id']
    assert portfolio_optimization.name == data['name']
    assert portfolio_optimization.optimism == data['optimism']
    assert portfolio_optimization.user == user
    assert portfolio_optimization.min_disposed_to_lose == data.get(
        'min_disposed_to_lose'
    )
    assert portfolio_optimization.assetoptimization_set.all().count() == 0


@pytest.mark.django_db
def test_create_or_update_portfolio_optimization_update_create():
    asset = baker.make('Asset')
    user = baker.make('User')
    portfolio_optimization = baker.make('PortfolioOptimization')

    data = {
        "id": portfolio_optimization.id,
        "name": "My first optimization",
        "optimism": 50,
        "user": user.id,
        "min_disposed_to_lose": 80.3,
        "asset_optimizations": [
            {
                "asset": asset.id,
                "min_to_invest": 20,
                "max_to_invest": 40
            }
        ]
    }
    serializer = RequestCreatePortfolioOptimizationSerializer(data=data)
    assert serializer.is_valid()
    portfolio_optimization = create_or_update_portfolio_optimization(
        serializer
    )
    assert portfolio_optimization.id == data['id']
    assert portfolio_optimization.optimism == data['optimism']
    assert portfolio_optimization.name == data['name']
    assert portfolio_optimization.user == user
    assert portfolio_optimization.min_disposed_to_lose == data.get(
        'min_disposed_to_lose'
    )
    assert portfolio_optimization.assetoptimization_set.all().count() == 1

    asset_optimization = portfolio_optimization.assetoptimization_set.last()
    assert asset_optimization.asset_id == data.get(
        'asset_optimizations'
    )[0]['asset']
    assert asset_optimization.min_to_invest == data.get(
        'asset_optimizations'
    )[0]['min_to_invest']
    assert asset_optimization.max_to_invest == data.get(
        'asset_optimizations'
    )[0]['max_to_invest']


@pytest.mark.django_db
def test_set_milestone_model_restrictions():
    asset = baker.make('Asset')
    milestone = baker.make('Milestone')
    asset_milestone = baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        deepest_down=-10
    )
    model = GEKKO()

    variables = {}
    variables[asset_milestone.asset_id] = model.Var()

    equation = set_milestone_model_restrictions(
        [asset_milestone],
        variables,
        model,
        1000
    )
    assert equation.value == '((v1)*(0.9))>1000'


@pytest.mark.django_db
def test_set_milestone_model_restrictions_none():
    asset = baker.make('Asset')
    milestone = baker.make('Milestone')
    model = GEKKO()

    variables = {}
    variables[asset.id] = model.Var()

    equation = set_milestone_model_restrictions(
        [],
        variables,
        model,
        1000
    )
    assert equation is None


@pytest.mark.django_db
def test_set_milestone_model_restrictions_assets_1():
    asset1 = baker.make('Asset')
    asset2 = baker.make('Asset')
    milestone = baker.make('Milestone')
    asset1_milestone = baker.make(
        'AssetMilestone',
        asset=asset1,
        milestone=milestone,
        deepest_down=-10
    )
    asset2_milestone = baker.make(
        'AssetMilestone',
        asset=asset2,
        milestone=milestone,
        deepest_down=-20
    )
    model = GEKKO()

    variables = {}
    variables[asset1_milestone.asset_id] = model.Var()
    variables[asset2_milestone.asset_id] = model.Var()

    asset_milestones = [asset1_milestone, asset2_milestone]

    equation = set_milestone_model_restrictions(
        asset_milestones,
        variables,
        model,
        1000
    )
    assert equation.value == '(((v1)*(0.9))+((v2)*(0.8)))>1000'


@pytest.mark.django_db
def test_set_milestone_model_restrictions_assets_2():
    asset1 = baker.make('Asset')
    asset2 = baker.make('Asset')
    milestone = baker.make('Milestone')
    asset1_milestone = baker.make(
        'AssetMilestone',
        asset=asset1,
        milestone=milestone,
        deepest_down=0
    )
    asset2_milestone = baker.make(
        'AssetMilestone',
        asset=asset2,
        milestone=milestone,
        deepest_down=-20
    )
    model = GEKKO()

    variables = {}
    variables[asset1_milestone.asset_id] = model.Var()
    variables[asset2_milestone.asset_id] = model.Var()

    asset_milestones = [asset1_milestone, asset2_milestone]
    equation = set_milestone_model_restrictions(
        asset_milestones,
        variables,
        model,
        1000
    )
    assert equation.value == '(((v1)*(1.0))+((v2)*(0.8)))>1000'


@pytest.mark.django_db
def test_set_milestone_model_restrictions_assets_3():
    asset1 = baker.make('Asset')
    asset2 = baker.make('Asset')
    milestone = baker.make('Milestone')
    asset1_milestone = baker.make(
        'AssetMilestone',
        asset=asset1,
        milestone=milestone,
        deepest_down=None
    )
    asset2_milestone = baker.make(
        'AssetMilestone',
        asset=asset2,
        milestone=milestone,
        deepest_down=-20
    )
    model = GEKKO()

    variables = {}
    variables[asset1_milestone.asset_id] = model.Var()
    variables[asset2_milestone.asset_id] = model.Var()

    asset_milestones = [asset1_milestone, asset2_milestone]
    equation = set_milestone_model_restrictions(
        asset_milestones,
        variables,
        model,
        1000
    )
    assert equation.value == '((v2)*(0.8))>1000'


def test_set_asset_optimization_restrictions():
    model = GEKKO()
    variable = model.Var()
    response = set_asset_optimization_restrictions(
        model,
        variable,
        100,
        10,
        50,
    )

    assert response['min_percentage_to_invest'].value == 'v1>=10.0'
    assert response['max_percentage_to_invest'].value == 'v1<=50.0'
    assert response['amount_to_invest'] is None
    assert response['no_zero'].value == 'v1>=0'


def test_set_asset_optimization_restrictions_amount_to_invest():
    model = GEKKO()
    variable = model.Var()
    response = set_asset_optimization_restrictions(
        model,
        variable,
        100,
        10,
        50,
        20,
    )

    assert response['min_percentage_to_invest'].value == 'v1>=10.0'
    assert response['max_percentage_to_invest'].value == 'v1<=50.0'
    assert response['amount_to_invest'].value == 'v1=20'
    assert response['no_zero'].value == 'v1>=0'


def test_set_asset_optimization_restrictions_total_to_invest():
    model = GEKKO()
    variable = model.Var()
    response = set_asset_optimization_restrictions(
        model,
        variable,
        4500,
        10,
        50,
    )
    assert response['min_percentage_to_invest'].value == 'v1>=450.0'
    assert response['max_percentage_to_invest'].value == 'v1<=2250.0'
    assert response['amount_to_invest'] is None
    assert response['no_zero'].value == 'v1>=0'


def test_set_total_amount_to_invest_restriction():

    model = GEKKO()
    variables = {
        1: model.Var(),
        2: model.Var(),
    }
    equation = set_total_amount_to_invest_restriction(
        model,
        1000,
        variables,
    )
    assert equation.value == '((0+v1)+v2)=1000'


@pytest.mark.django_db
def test_get_total_performance_abundance_average():
    milestone = baker.make(
        'Milestone',
        milestone_type=MILESTONE_ABUNDANCE,
        end=datetime.today()
    )
    asset = baker.make('Asset')
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=100,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=50,
    )
    average = get_total_performance_abundance_average(asset)
    assert average == 75


@pytest.mark.django_db
def test_get_total_performance_abundance_average_none():
    baker.make(
        'Milestone',
        milestone_type=MILESTONE_ABUNDANCE,
        end=datetime.today()
    )
    asset = baker.make('Asset')
    average = get_total_performance_abundance_average(asset)
    assert average is None


@pytest.mark.django_db
def test_get_total_performance_abundance_average_none_2():
    milestone = baker.make(
        'Milestone',
        milestone_type=MILESTONE_ABUNDANCE,
        end=datetime.today()
    )
    asset = baker.make('Asset')
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=None,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=50,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=100,
    )
    average = get_total_performance_abundance_average(asset)
    assert average == 75


@pytest.mark.django_db
def test_get_total_performance_abundance_average_none_3():
    milestone = baker.make(
        'Milestone',
        milestone_type=MILESTONE_ABUNDANCE,
        end=datetime.today()
    )
    asset = baker.make('Asset')
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=None,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=100,
    )
    average = get_total_performance_abundance_average(asset)
    assert average == 100


@pytest.mark.django_db
def test_get_total_performance_abundance_average_none_4():
    milestone = baker.make(
        'Milestone',
        milestone_type=MILESTONE_ABUNDANCE,
        end=None
    )
    asset = baker.make('Asset')
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=None,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=100,
    )
    average = get_total_performance_abundance_average(asset)
    assert average is None


@pytest.mark.django_db
def test_get_total_performance_crisis_average():
    milestone = baker.make(
        'Milestone',
        milestone_type=MILESTONE_CRISIS,
        end=datetime.today()
    )
    asset = baker.make('Asset')
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=100,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=50,
    )
    average = get_total_performance_crisis_average(asset)
    assert average == 75


@pytest.mark.django_db
def test_get_total_performance_crisis_average_none():
    baker.make(
        'Milestone',
        milestone_type=MILESTONE_CRISIS,
        end=datetime.today()
    )
    asset = baker.make('Asset')
    average = get_total_performance_crisis_average(asset)
    assert average is None


@pytest.mark.django_db
def test_get_total_performance_crisis_average_none_2():
    milestone = baker.make(
        'Milestone',
        milestone_type=MILESTONE_CRISIS,
        end=datetime.today()
    )
    asset = baker.make('Asset')
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=None,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=50,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=100,
    )
    average = get_total_performance_crisis_average(asset)
    assert average == 75


@pytest.mark.django_db
def test_get_total_performance_crisis_average_none_3():
    milestone = baker.make(
        'Milestone',
        milestone_type=MILESTONE_CRISIS,
        end=datetime.today()
    )
    asset = baker.make('Asset')
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=None,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=100,
    )
    average = get_total_performance_crisis_average(asset)
    assert average == 100


@pytest.mark.django_db
def test_get_total_performance_crisis_average_none_4():
    milestone = baker.make(
        'Milestone',
        milestone_type=MILESTONE_CRISIS,
        end=None
    )
    asset = baker.make('Asset')
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=None,
    )
    baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
        total_performance=100,
    )
    average = get_total_performance_crisis_average(asset)
    assert average is None
