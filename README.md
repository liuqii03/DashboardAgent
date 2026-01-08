Dashboard Deployment Commands
# Run local test with the Dashboard agent
python3 -m my_agent.deployment.local

# Create a new deployment
python3 -m my_agent.deployment.remote --create

# List all deployments
python3 -m my_agent2.deployment.remote --list

# Delete a deployment
python3 -m my_agent2.deployment.remote --delete --resource_id <RESOURCE_ID>

# Create a session for a deployed agent
python3 -m my_agent.deployment.remote --create_session --resource_id 3498466779187904512 --user_id test_user

# List sessions for a user
python3 -m my_agent.deployment.remote --list_sessions --resource_id 3498466779187904512 --user_id test_user

# Get session details
python3 -m my_agent.deployment.remote --get_session --resource_id 3976974239596019712 --user_id test_user --session_id 2972819681884241920

# Send a message to deployed agent
python3 -m my_agent.deployment.remote --send  --resource_id 3976974239596019712 --user_id test_user --session_id 8902934491224342528 --message “Find me a car in Seri Kembangan”
