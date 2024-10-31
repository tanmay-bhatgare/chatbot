import asyncio
from typing import Any
import httpx


async def getModelsName():
    """return the list of model name

    Returns:
        list: a list containing the model name
    """
    modelName = []
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:11434/api/tags")
        responseJson = response.json()
        for model in responseJson["models"]:
            modelName.append(model["name"])
    return modelName


async def askModel(
    modelName: str, prompt: str, stream: bool = False, temperature: float = 0.3
) -> dict[str, Any] | dict[str, str] | dict[str, str]:
    """return a model's json formatted response

    Args:
        modelName (str): name of the model
        question (str): user question
        stream (bool, optional): whether to return a response in parts or not. Defaults to False.
        temperature (float, optional): randomness of model. Defaults to 0.3.

    Returns:
        dict: model's json formatted response
    """
    try:
        async with httpx.AsyncClient(timeout=2000) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": modelName,
                    "prompt": f"""
                    Please respond to my questions in Markdown format. If the response requires detail, use structured Markdown with headers, bullet points, and code blocks as needed. If the response is simple, such as a greeting, provide a brief Markdown response. Don't repeat the prompt you have given. don't use code-block(```), use only ![Image](Image URL) for rendering images.
                    Question: {prompt}
                        """,
                    "stream": stream,
                    "options": {"temperature": temperature},
                },
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to generate response; reason => {response.text}"
                }
    except httpx.TimeoutException as e:
        print(e)
        return {"error": "Request timed out"}
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code}")
        return {"Error": f"Request failed with status code, {e.response.status_code}"}


if __name__ == "__main__":
    print(asyncio.run(askModel("mistral", "Hello")))
