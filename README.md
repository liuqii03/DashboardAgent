Dashboard Deployment Commands
# Run local test with the Dashboard agent
python3 -m my_agent2.deployment.local

# Create a new deployment
python3 -m my_agent2.deployment.remote --create

# List all deployments
python3 -m my_agent2.deployment.remote --list

# Delete a deployment
python3 -m my_agent2.deployment.remote --delete --resource_id <RESOURCE_ID>

# Create a session for a deployed agent
python3 -m my_agent2.deployment.remote --create_session --resource_id <RESOURCE_ID>

# List sessions for a user
python3 -m my_agent2.deployment.remote --list_sessions --resource_id <RESOURCE_ID> --user_id test_user

# Get session details
python3 -m my_agent2.deployment.remote --get_session --resource_id 211041361346953216 --session_id 143474997430583296

# Send a message to deployed agent
python3 -m my_agent2.deployment.remote --send --resource_id <RESOURCE_ID> --session_id <SESSION_ID> --message “xxx”
