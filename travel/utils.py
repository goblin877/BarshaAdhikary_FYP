import cohere  # Ensure this is imported to use the Cohere client

def generate_itinerary_with_cohere(prompt):
    try:
        print("=== Prompt sent to Cohere ===")
        print(prompt)

        # Replace the API key with your actual Cohere API key
        co = cohere.Client("NrW4mSl720QMFJplq1ARyfqzUKtTeoLjvgbHZC7N")  # Your Cohere API key (keep it secure)

        # Sending the prompt to Cohere to generate a response
        response = co.generate(
            model='command',  # You can choose the model that fits your needs
            prompt=prompt,
            max_tokens=1000,  # Adjust token limit as necessary
            temperature=0.7  # Control creativity
        )

        print("=== Cohere response ===")
        print(response.generations[0].text)

        return response.generations[0].text.strip()  # Return the generated itinerary text

    except Exception as e:
        print("=== Cohere Error ===")
        print(e)
        return "Error generating itinerary with Cohere."  # In case of error, return a message
