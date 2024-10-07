## Running the Application

Follow these steps to set up and run the string comparison API:

1. **Clone the repository** into your target folder:
    ```bash
    git clone https://github.com/alvarodeamos/string-comparison-api.git
    ```

2. **Move the `names_dataset.csv` file** to the **`string-comparison-api`** folder (root of the app). This file will be automatically loaded into the database when the app is started.

3. **Navigate to the main app folder**:
    ```bash
    cd string-comparison-api
    ```

4. **Ensure Docker is running** on your machine. Then, build and run the Docker containers to set up the database and the application:
    ```bash
    docker-compose build
    docker-compose up
    ```

This will start the application and set up the database.



## Test name similarity endpoint

You can use the following Python script to test the `/similarity` endpoint of the API. This script sends a GET request to the API, checks for a successful response, and then prints the names along with their similarity scores.

```python
import requests

def test_name_similarity(name: str, threshold: int, base_url: str = "http://localhost:8000"):
    url = f"{base_url}/similarity?input_name={name}&threshold={threshold}"
    
    try:
        result = requests.get(url)
        # raises HTTPError if response code not 200
        result.raise_for_status()
        # get response as JSON         
        final_dictionary = result.json()
        # print results
        for k, v in final_dictionary.items():
            print(f"{k}: {v['full_name']}, Similarity: {v['similarity']}")    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except ValueError:
        print("Invalid JSON response received from the API")

if __name__ == "__main__":
    input_name = "Ana Fernández"
    input_threshold = 91
    test_name_similarity(name=input_name, threshold=input_threshold)
