from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_experimental.synthetic_data import create_data_generation_chain
from langchain_experimental.tabular_synthetic_data.openai import create_openai_data_generator
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_PREFIX, SYNTHETIC_FEW_SHOT_SUFFIX
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

load_dotenv()


class MedicalBilling(BaseModel):
    patient_id: int
    patient_name: str
    diagnosis_code: str
    procedure_code: str
    total_charge: float
    insurance_claim_amount: float


def gen_text():
    """
    自动生成文本
    """
    model = ChatOpenAI(temperature=0.8)
    chain = create_data_generation_chain(llm=model)
    rsp = chain(inputs={
        "fields": {"颜色": ["蓝色", "黄色"]},
        "preferences": {
            "style": "让它像诗歌一样"
        }
    })
    print(rsp)


def gen_struct_obj():
    """
    自动生成结构化数据
    """
    examples = [
        {
            "example": "Patient ID: 123456, Patient Name: John Doe, Diagnosis Code: J20.9, Procedure Code: 99203, Total Charge: $500, Insurance Claim Amount: $350"},
        {
            "example": "Patient ID: 789012, Patient Name: Johnson Smith, Diagnosis Code: M54.5, Procedure Code: 99213, Total Charge: $150, Insurance Claim Amount: $120"},
        {
            "example": "Patient ID: 345678, Patient Name: Emily Stone, Diagnosis Code: E11.9, Procedure Code: 99214, Total Charge: $300, Insurance Claim Amount: $250"},
    ]

    OPENAI_TEMPLATE = PromptTemplate(input_variables=["example"], template="{example}")

    prompt_template = FewShotPromptTemplate(
        prefix=SYNTHETIC_FEW_SHOT_PREFIX,
        examples=examples,
        suffix=SYNTHETIC_FEW_SHOT_SUFFIX,
        input_variables=["subject", "extra"],
        example_prompt=OPENAI_TEMPLATE,
    )

    synthetic_data_generator = create_openai_data_generator(
        output_schema=MedicalBilling,
        llm=ChatOpenAI(temperature=1),  # 使用API代理服务提高访问稳定性
        prompt=prompt_template,
    )

    synthetic_results = synthetic_data_generator.generate(
        subject="medical_billing",
        extra="the name must be chosen at random. Make it something you wouldn't normally choose.",
        runs=2,
    )
    print(synthetic_results)


if __name__ == '__main__':
    gen_struct_obj()
