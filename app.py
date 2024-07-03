import streamlit as st
from langchain.schema import Document
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import OpenSearchVectorSearch
import pandas as pd
import yaml

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    config = load_config('config.yaml')
    opensearch_url = config['opensearch_url']
    http_auth = (config['http_auth']['username'], config['http_auth']['password'])
    service_endpoint = config['service_endpoint']
    compartment_id = config['compartment_id']
    emb_llm_id = config['emb_llm_id']
    gen_llm_id = config['gen_llm_id']
    
    st.title('OpenSearch Vector Search App🔍')
    with st.expander("ベクトルデータは以下の2リンクの情報を使用しています"):
        st.markdown("[Oracle Cloud Infrastructure - コンピュート概要](https://docs.oracle.com/ja-jp/iaas/Content/Compute/Concepts/computeoverview.htm)")
        st.markdown("[Oracle Cloud Compute - FAQ](https://www.oracle.com/jp/cloud/compute/faq/)")
    
    user_input = st.text_input('検索ワードを入力してください')
    k_value = st.selectbox(
        'k-NN (k近傍法)の値',
        range(1, 11),
        index=2  # デフォルトは3（0から数えて3番目）
    )
    
    embeddings = OCIGenAIEmbeddings(
        model_id=emb_llm_id,
        service_endpoint=service_endpoint,
        compartment_id=compartment_id,
    )
    
    docsearch = OpenSearchVectorSearch(
        index_name="vm_*",
        embedding_function=embeddings,
        opensearch_url=opensearch_url,
        http_auth=http_auth,
    )
    
    if st.button('実行'):
        if not user_input:
            st.write('テキストが入力されていません。')
            return
        st.write(f'入力されたテキスト: {user_input}')
        docs = docsearch.similarity_search(user_input, k=k_value)
        
        data = []
        for doc in docs:
            page_content = doc.page_content.replace('\n', '<br>').replace('\t', '&#009;')
            source = doc.metadata['source']
            data.append({'page_content': page_content, 'source': source})
        
        df = pd.DataFrame(data)
        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

if __name__ == '__main__':
    main()
