import streamlit as st
from langchain.schema import Document
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
import pandas as pd
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

def main():
    st.title('社内文書検索テスト🔍')
    user_input = st.text_input('検索ワードを入力してください')
    # k_value = st.selectbox(
    #     'k-NN (k近傍法)の値',
    #     range(1, 11),
    #     index=2  # デフォルトは3（0から数えて3番目）
    # )
    embeddings = OCIGenAIEmbeddings(
        auth_type="RESOURCE_PRINCIPAL",
        model_id=emb_llm_id,
        service_endpoint=service_endpoint,
        compartment_id=compartment_id,
    )
    docsearch = OpenSearchVectorSearch(
        index_name="docsearch",
        embedding_function=embeddings,
        opensearch_url=opensearch_url,
        http_auth=http_auth,
    )
    llm = ChatOCIGenAI(
        auth_type="RESOURCE_PRINCIPAL",
        model_id=gen_llm_id,
        service_endpoint=service_endpoint,
        compartment_id=compartment_id,
        model_kwargs={"temperature": 0.7, "max_tokens": 4000},
    )

    if st.button('実行'):
        if not user_input:
            st.write('テキストが入力されていません。')
            return
        st.write(f'入力されたテキスト: {user_input}')
        # docs = docsearch.similarity_search(
        #     user_input, k=k_value)
        retriever = docsearch.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        # st.write("こんちにわ！")

        # prompt_template_qa = """あなたは親切で優しいアシスタントです。丁寧に、日本語でお答えください！
        # 質問に該当する答えが見つかった場合は、該当する全てのパスを返却してください。

        # {context}

        # 質問: {question}
        # 回答（日本語）:"""

        prompt_template_qa = """あなたは親切で丁寧なアシスタントです。以下の質問に対して、日本語で詳しくわかりやすくお答えください。
        質問に該当する答えが見つかった場合は、すべての関連する情報源（パス）も併せて提供してください。
        該当する情報が見つからない場合や、関係のない質問については「申し訳ございません、該当する情報が見つかりませんでした」と答えてください。

        文脈:
        {context}

        質問:
        {question}

        回答（日本語）:"""

        prompt_qa = PromptTemplate(
            template=prompt_template_qa,
            input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": prompt_qa}

        QA = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs=chain_type_kwargs,
            return_source_documents=True,
            verbose=True
        )
        tret = QA.invoke(user_input)
        # st.write("処理完了")
        st.write(tret)


        # st.write(docs[0])
        # data = []
        # for doc in docs:
        #     # page_content = doc.page_content
        #     page_content = doc.page_content.replace('\n', '<br>').replace('\t', '&#009;')
        #     source = doc.metadata['source']
        #     data.append({'page_content': page_content, 'source': source})
        # df = pd.DataFrame(data)
        # st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
if __name__ == '__main__':
    main()
