import sys
import os
from utils import ensureProduct,getAdminPass,getApiToken,ensureEngagement,uploadTestResults,ensureDefectDojoRunning
# from utils import requestsDebug

path = sys.argv[1]
engagement = sys.argv[2] + "-" + sys.argv[3]
languages = sys.argv[3].split(',')
semgrep_configs = list(map(lambda language: '--config auto' if language == 'auto' else f"--config p/{language}", languages))
project = path.split('/').pop()

print(path, project)

ensureDefectDojoRunning()

admin_password = getAdminPass()
print(f"Admin pass: {admin_password}")

api_token = getApiToken(admin_password)
print(f"API token: {api_token}")

product_id = ensureProduct(project, api_token)
print(f"Product id: {product_id}")

engagement_id = ensureEngagement(engagement, api_token, product_id)
print(f"Engagement id: {engagement_id}")

print("Running tests...")

os.system(f"semgrep scan {path} {' '.join(semgrep_configs)} --json --output tmp/semgrep.json")
uploadTestResults('tmp/semgrep.json', engagement_id, 'Semgrep JSON Report', api_token)

if 'javascript' in languages:
    print("Running njsscan")
    os.system(f"njsscan {path} --sarif --output tmp/njsscan.sarif")
    uploadTestResults('tmp/njsscan.sarif', engagement_id, 'SARIF', api_token)


