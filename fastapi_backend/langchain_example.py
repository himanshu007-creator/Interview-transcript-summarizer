"""
Example usage of LangChain components with OpenRouter
"""
import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda, RunnableSequence, RunnableParallel
from langchain_openai import ChatOpenAI

from .openrouter import ChatOpenRouter

load_dotenv()


def create_simple_chain():
    """Create a simple LangChain chain with OpenRouter."""
    
    # Create the model
    model = ChatOpenRouter(model_name="anthropic/claude-3.5-sonnet")
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}")
    ])
    
    # Create output parser
    output_parser = StrOutputParser()
    
    # Create the chain
    chain = prompt | model | output_parser
    
    return chain


def create_parallel_chain():
    """Create a parallel chain example."""
    
    model = ChatOpenRouter(model_name="anthropic/claude-3.5-sonnet")
    
    # Create different prompts
    joke_prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
    poem_prompt = ChatPromptTemplate.from_template("Write a short poem about {topic}")
    
    # Create parallel chains
    parallel_chain = RunnableParallel({
        "joke": joke_prompt | model | StrOutputParser(),
        "poem": poem_prompt | model | StrOutputParser()
    })
    
    return parallel_chain


def create_sequence_chain():
    """Create a sequence chain example."""
    
    model = ChatOpenRouter(model_name="anthropic/claude-3.5-sonnet")
    
    # First step: generate a topic
    topic_prompt = ChatPromptTemplate.from_template(
        "Generate a random topic related to {category}"
    )
    
    # Second step: write about the topic
    content_prompt = ChatPromptTemplate.from_template(
        "Write a brief explanation about: {topic}"
    )
    
    # Create sequence chain
    sequence_chain = RunnableSequence(
        topic_prompt | model | StrOutputParser(),
        RunnableLambda(lambda topic: {"topic": topic}),
        content_prompt | model | StrOutputParser()
    )
    
    return sequence_chain


# Example usage functions
async def run_simple_example():
    """Run simple chain example."""
    chain = create_simple_chain()
    result = await chain.ainvoke({"input": "What is FastAPI?"})
    return result


async def run_parallel_example():
    """Run parallel chain example."""
    chain = create_parallel_chain()
    result = await chain.ainvoke({"topic": "programming"})
    return result


async def run_sequence_example():
    """Run sequence chain example."""
    chain = create_sequence_chain()
    result = await chain.ainvoke({"category": "technology"})
    return result