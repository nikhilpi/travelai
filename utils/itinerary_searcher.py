from langchain.utilities import GoogleSearchAPIWrapper
from langchain.document_loaders import UnstructuredURLLoader

base_locations = [
    "France",
    "Japan",
    "USA",
    "Thailand",
    "Italy",
    "Spain",
    "England",
    "UAE",
    "Singapore",
    "Netherlands",
    "Turkey",
    "Czech Republic",
    "Australia",
    "Brazil",
    "China",
    "Indonesia",
    "Morocco",
    "South Africa",
    "Hungary",
    "Canada"
]

top_travel_websites = [
    "https://www.lonelyplanet.com",
    "https://www.tripadvisor.com",
    "https://www.fodors.com",
    "https://www.frommers.com",
    "https://www.roughguides.com",
    "https://www.afar.com",
    "https://www.cntraveler.com",
    "https://www.nationalgeographic.com/travel",
    "https://www.travelandleisure.com",
    "https://www.theculturetrip.com",
    "https://www.thepointsguy.com",
    "https://www.nomadicmatt.com",
    "https://www.ricksteves.com",
    "https://www.expertvagabond.com",
    "https://www.atlasobscura.com",
    "https://www.iamaileen.com",
    "https://www.roadtrippers.com",
    "https://www.tripsavvy.com",
    "https://www.bucketlistly.blog",
    "https://www.thecrazytourist.com"
]

def query_generator(location):
    queries = []
    queries.append(location + " itinerary")
    queries.append(location + " 3 day itinerary")
    queries.append(location + " 5 day itinerary")
    queries.append(location + " 7 day itinerary")
    queries.append(location + " 14 day itinerary")
    for site in top_travel_websites:
        queries.append(location + " itinerary site:" + site)
    return queries

def get_itinerary_urls(location):
    queries = query_generator(location)
    search = GoogleSearchAPIWrapper()
    results = []
    for query in queries:
        results += search.results(query, 5)
    return results

def download_itinerary(url):
    loader = UnstructuredURLLoader(urls=[url])
    data = loader.load()
    return data[0]
    
