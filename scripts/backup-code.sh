# In the remote server
docker exec 3151e306dda8 pg_dump -U admin economic_system > 20200303

# In the local server
scp economic_system@economicapp.io:src/economic_system/backups/20200303 backups/.

# In the local server
docker exec -it <postgres_container_id> bash

# In my local postgres container
psql -U admin -d economic_system

# In my postgres database that I want to restore
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO admin;
GRANT ALL ON SCHEMA public TO public;
\q

# In the local postgres container
cd backups
psql -U admin -d economic_system < 20200304



