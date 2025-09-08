from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from typing import List

class field_data(BaseModel):
    field: List[str] = Field(description="Mention the category: Job Post, Freelance Post, Internship Post, or Normal Post")
    keyword: List[str] = Field(description="Extract the main field/domain/technology/role/industry mentioned in the post")

class JFINclassifier:
    def __init__(self, post):
        load_dotenv()
        self.post=post

    def model(self):
        gemini_model=ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
        # gemini_model=ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite-preview-06-17")
        return gemini_model
    
    def data_parser(self):
        parser=PydanticOutputParser(pydantic_object=field_data)
        # print(parser.get_format_instructions())
        return parser

    def template(self):
        parser = self.data_parser()
        template = PromptTemplate(
            template=(
                "You are a classification assistant. Your task is to analyze the given social media or professional post "
                "and perform the following:\n\n"
                "1. Classify the post into one of the following categories:\n"
                "   - Job Post: A post offering full-time or part-time employment.\n"
                "   - Freelance Post: A post offering or requesting freelance/project-based work.\n"
                "   - Internship Post: A post offering or seeking internships.\n"
                "   - Normal Post: Any post that doesn't fit the above categories.\n\n"
                "2. Extract relevant **keywords** related to the academic field, role, industry, or skills mentioned in the post "
                "(e.g., 'Data Analyst', 'Python', 'SaaS').\n\n"
                "Post:\n{post}\n\n"
                "Provide your response strictly in the following format:\n\n"
                "{format_instruction}"
            ),
            input_variables=['post'],
            partial_variables={'format_instruction':parser.get_format_instructions()}
        )
        return template
    
    def chain(self):
        template = self.template()
        model = self.model()
        parser = self.data_parser()

        chain = template | model | parser
        result=chain.invoke({"post": self.post})

        return result

if __name__ == '__main__':
    sample_post = """

                Dear Friends/ Recruiters/ everyone ,

                I’m available to join immediately.

                I’m currently seeking new opportunities(immediately)as a SAP MM / S/4HANA Consultant. With 3.5 years of strong SAP MM experience (S/4HANA).

                📩 DM (+91 6380335462) me or comment below.\

                ✅ Worked with Cognizant

                If you’re hiring or can refer me, I’d truly appreciate your support!

                """

    classifier = JFINclassifier(sample_post)
    chain = classifier.chain()
    print(chain)
