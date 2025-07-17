from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.credentials import Credentials

#  Step 1: Only pass API key and URL here
creds = Credentials(
    url="https://us-south.ml.cloud.ibm.com",
    api_key= "your ibm api key make sure project has watsonx machine learning service assoicated"
)

# Step 2: Pass project_id into the Model call
model = ModelInference(
    model_id="ibm/granite-3-2b-instruct",  #  granite 3.3B model
    credentials=creds,
    project_id = "your project id ",

    params={
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 1024,
        GenParams.TEMPERATURE: 0.5
    }
)

def query_watsonx(prompt: str):
    response = model.generate(prompt)
    return response['results'][0]['generated_text']
