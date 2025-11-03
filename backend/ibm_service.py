import os
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

load_dotenv()

class IBMService:
    def __init__(self):
        self.api_key = os.getenv("IBM_API_KEY")
        self.project_id = os.getenv("IBM_PROJECT_ID")
        self.url = os.getenv("IBM_URL")
        
        self.credentials = {
            "url": self.url,
            "apikey": self.api_key
        }
        
        self.model_id = "ibm/granite-3-8b-instruct"
        
        self.parameters = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 2000,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.TEMPERATURE: 0.7,
            GenParams.TOP_K: 50,
            GenParams.TOP_P: 1
        }
    
    def generate_code(self, prompt: str) -> str:
        """Generate code based on user prompt"""
        model = Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.credentials,
            project_id=self.project_id
        )
        
        full_prompt = f"""You are a code generation assistant. Generate clean, well-commented code.

User Request: {prompt}

Generate only the code without any additional explanation:"""
        
        response = model.generate_text(prompt=full_prompt)
        return response
    
    def generate_test_cases(self, code: str) -> str:
        """Generate test cases for given code"""
        model = Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.credentials,
            project_id=self.project_id
        )
        
        full_prompt = f"""You are a test case generation assistant. Generate comprehensive test cases.

Code:
{code}

Generate test cases in a clear format with test case name, input, expected output, and test type:"""
        
        response = model.generate_text(prompt=full_prompt)
        return response
    
    def fix_bug(self, code: str, bug_description: str) -> str:
        """Fix bugs in the provided code"""
        model = Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.credentials,
            project_id=self.project_id
        )
        
        full_prompt = f"""You are a bug fixing assistant. Fix the bug and explain the fix.

Code with Bug:
{code}

Bug Description: {bug_description}

Provide the fixed code and explanation:"""
        
        response = model.generate_text(prompt=full_prompt)
        return response
    
    def requirements_to_code(self, requirements: str) -> dict:
        """Generate documentation, code, and test cases from requirements"""
        model = Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.credentials,
            project_id=self.project_id
        )
        
        # Generate documentation
        doc_prompt = f"""Generate project documentation for the following requirements:

Requirements: {requirements}

Provide: Project Overview, Architecture, Components, and Implementation Plan"""
        
        documentation = model.generate_text(prompt=doc_prompt)
        
        # Generate code
        code_prompt = f"""Generate complete code implementation for:

Requirements: {requirements}

Provide clean, production-ready code:"""
        
        code = model.generate_text(prompt=code_prompt)
        
        # Generate test cases
        test_prompt = f"""Generate comprehensive test cases for:

Requirements: {requirements}

Code:
{code}

Provide detailed test cases:"""
        
        test_cases = model.generate_text(prompt=test_prompt)
        
        return {
            "documentation": documentation,
            "code": code,
            "test_cases": test_cases
        }
    
    def generate_uml(self, requirements: str) -> str:
        """Generate UML diagram description"""
        model = Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.credentials,
            project_id=self.project_id
        )
        
        full_prompt = f"""Generate a PlantUML code for class diagram based on:

Requirements: {requirements}

Provide only PlantUML code starting with @startuml and ending with @enduml:"""
        
        response = model.generate_text(prompt=full_prompt)
        return response

ibm_service = IBMService()