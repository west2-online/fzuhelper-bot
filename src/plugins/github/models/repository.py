from pydantic import BaseModel, HttpUrl


class Repository(BaseModel):
    """GitHub repository model"""

    name: str
    full_name: str
    private: bool
    html_url: HttpUrl
