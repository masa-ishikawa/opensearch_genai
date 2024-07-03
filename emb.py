from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
import yaml


def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config('config.yaml')
opensearch_url = config['opensearch_url']
http_auth = (config['http_auth']['username'], config['http_auth']['password'])
service_endpoint = config['service_endpoint']
compartment_id = config['compartment_id']
emb_llm_id = config['emb_llm_id']
gen_llm_id = config['gen_llm_id']

embeddings = OCIGenAIEmbeddings(
    model_id=emb_llm_id,
    service_endpoint=service_endpoint,
    compartment_id=compartment_id,
)

text_files = [
    {"path": "./ocifaq.txt", "index_name": "vm_faq", "chunk_size": 500, "chunk_overlap": 50},
    {"path": "./ocidoc.txt", "index_name": "vm_doc", "chunk_size": 500, "chunk_overlap": 50},
    {"path": "./docsearch.txt", "index_name": "docsearch", "chunk_size": 300, "chunk_overlap": 30},
]

for text_file in text_files:
    loader = TextLoader(text_file["path"], encoding='utf-8')
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"],
        chunk_size=text_file["chunk_size"],
        chunk_overlap=text_file["chunk_overlap"],
        length_function=len,
        is_separator_regex=False,
    )
    docs = text_splitter.split_documents(documents)

    max_chunk_size = 95
    for chunk_start in range(0, len(docs), max_chunk_size):
        chunk_docs = docs[chunk_start:chunk_start + max_chunk_size]
        docsearch = OpenSearchVectorSearch.from_documents(
            chunk_docs, embeddings, opensearch_url=opensearch_url, http_auth=http_auth,
            use_ssl=False,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            index_name=text_file["index_name"],
        )
print("finish")
