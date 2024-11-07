def get_gender_prompt(author_firstname, author_lastname):
    return f"""Given the names of the author, please identify the likely gender of the author.
    Provide the gender as either "male", "female", "other", or "not retrievable".
    Also, include a reasoning for each author based on the name provided.
    The name of the author is: {author_firstname} {author_lastname}.
    Please return the response in **strict JSON format only**, with no additional text.
    Use the following structure:
    {{
        "author": {{
            "first_name": "{author_firstname}",
            "last_name": "{author_lastname}",
            "gender": "male/female/other/not retrievable",
            "reasoning": "Explanation for the gender determination of the author."
        }}
    }}
    """

