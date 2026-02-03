from os import environ
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from pydantic import SecretStr
from prompts.instagram import instagram_prompt
from prompts.linkedin import linkedin_prompt
import time

llm = ChatOpenAI(
    model="google/gemma-3-27b-it",
    api_key=SecretStr(environ["OPENAI_API_KEY"]),
    base_url=environ["OPENAI_BASE_URL"],
    temperature=0,
    streaming=True,
    max_completion_tokens=300,
)

parser = StrOutputParser()
instagram_chain = instagram_prompt | llm | parser
linkedin_chain = linkedin_prompt | llm | parser

parallel_chain = RunnableParallel(instagram=instagram_chain, linkedin=linkedin_chain)

topic = input("\ntopic: ")


begin_stream_time = time.perf_counter()
for c in parallel_chain.stream({"topic": topic}):
    print(c)

print("=" * 30)
end_stream_time = time.perf_counter()
print(f"stream parallel took {end_stream_time - begin_stream_time}")
print("=" * 30)

begin_invoke_time = time.perf_counter()
result = parallel_chain.invoke({"topic": topic})
end_invoke_time = time.perf_counter()

print("=" * 30)
print(result["instagram"])
print("=" * 30)
print(result["linkedin"])
print("=" * 30)
print(f"invoke parallel took {end_invoke_time - begin_invoke_time}")
