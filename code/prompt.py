def get_gender_prompt(author_firstname, author_lastname):
    return f"""Given the name of the author, please identify the likely gender of the author.
    Consider the following instructions:

    - Provide the gender as either "male", "female", "other", or "not retrievable".
    - Include a reasoning for each author based on the name provided.
    - For composed names (e.g., "Jose María", "Emma Charles"), consider the combined meaning, as such names may indicate gender differently than their individual parts would suggest.

    The first name of the author is: {author_firstname}.
    The last name of the author is: {author_lastname}.
   
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

