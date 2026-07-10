import os
from dotenv import load_dotenv

load_dotenv()

IBM_API_KEY   = os.getenv("IBM_API_KEY",    "eys7_ZBMltxg3g6BV1QJs1LlQjrl0EdqQq6Qrkl06oqu")
IBM_PROJECT_ID= os.getenv("IBM_PROJECT_ID", "90c777b2-09cc-43bc-8a85-9c0c6292786a")
IBM_MODEL_ID  = os.getenv("IBM_MODEL_ID",   "ibm/granite-4-h-small")
IBM_URL       = os.getenv("IBM_URL",        "https://eu-de.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29")
IBM_IAM_URL   = os.getenv("IBM_IAM_URL",    "https://iam.cloud.ibm.com/identity/token")
