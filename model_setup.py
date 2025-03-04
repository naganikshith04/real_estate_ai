from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
import os
from dotenv import load_dotenv

# Flag to track if AWS features are available
HAS_BEDROCK = False

# Only import boto3 if needed
try:
    import boto3
    from langchain_community.chat_models import BedrockChat
    HAS_BEDROCK = True
except ImportError:
    # boto3 not installed, AWS features will be disabled
    pass

load_dotenv()

class ModelSetup:
    def __init__(self):
        pass
    
    def get_openai_model(self):
        """
        Setup and return OpenAI's GPT-4o model
        """
        return ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def get_anthropic_model(self):
        """
        Setup and return Anthropic's Claude model
        """
        return ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0.2,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    def get_bedrock_claude(self):
        """
        Setup and return Claude via Amazon Bedrock
        """
        if not HAS_BEDROCK:
            raise ImportError("BedrockChat not available. Please install langchain-aws package.")
            
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        return BedrockChat(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            client=bedrock_runtime,
            model_kwargs={"temperature": 0.2, "max_tokens": 4000}
        )
    
    def get_bedrock_llama(self):
        """
        Setup and return Llama via Amazon Bedrock
        """
        if not HAS_BEDROCK:
            raise ImportError("BedrockChat not available. Please install langchain-aws package.")
            
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        return BedrockChat(
            model_id="meta.llama3-70b-instruct-v1:0",
            client=bedrock_runtime,
            model_kwargs={"temperature": 0.2, "max_tokens": 4000}
        )