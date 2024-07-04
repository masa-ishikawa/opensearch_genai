# OCI OpenSearchにおけるGenerativeAI用いたRAG構成


## 環境構築の流れ
* vcn作成
* compute立ち上げ
* computeの環境構築
* computeからembedding
* firewall穴あけ
* ダッシュボードログイン
* computeからアプリ起動
* 動作確認


## 各種コマンド
### cloudシェルから接続
```sh
VMのプライベートキーファイルをcloudシェル画面に貼り付けてアップロード
chmod 600 ssh-key-2024-07-04.key
ssh -i ssh-key-2024-07-04.key opc@<接続先public ip>
```

### gitインストール
```sh
sudo yum install git
```

### git clone
```sh
git clone https://github.com/masa-ishikawa/opensearch_genai.git
cd opensearch_genai
chmod +x *.sh
```

### pythonのビルドに必要な依存ファイルをインストール
```sh
./1_prepython.sh
```

### pythonインストール
```sh
./2_pythnobuild.sh
```


### pipインストール
```sh
./3_pip.sh

実行後、下記のコマンド結果のようになっていればOK
[opc@instance-20240704-1009 opensearch_genai]$ python -V
Python 3.12.4
[opc@instance-20240704-1009 opensearch_genai]$ pip -V
pip 24.1.1 from /home/opc/.local/lib/python3.12/site-packages/pip (python 3.12)
```

### pythonモジュールインスト
```sh
./4_module.sh
```

### アプリケーション設定ファイルの修正
```
config.yamlを開いて、以下をOCIコンソールから参照し更新する
・opensearch_url ⇒opensearchクラスタ画面のapiエンドポイント
・compartment_id ⇒対象コンパートメントのocid
```

### OCI設定ファイルの修正
```
OCIコンソールのユーザページから「APIキーの追加」を実行
APIキー・ペアの生成を選び、秘密キーと公開キーをDLする
下記手順を参考に、~/.oci/configを作成する
```
https://www.ashisuto.co.jp/db_blog/article/N0021_OracleCloud_20200626.html

### 特定ポートの穴あけ
```
以下のVCNのセキュリティリストを穴あけする：
・プライベートサブネットの5601,9200(opensearch)
・パブリックサブネットの8501(streamlit用)
```
```sh
続いて、VMのファイアウォール設定から穴あけする
sudo firewall-cmd --zone=public --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```


### embedding処理
```sh
事前に用意したtxtファイルに対して、oci generative apiを使ってopensearchに格納
python emb.py
```

### opensearchダッシュボードの確認
```sh
ssh -C -v -t -L 127.0.0.1:5601:(dashboard private ip):5601 -L 127.0.0.1:9200:(endpoint private ip):9200 opc@(踏み台のpublic ip) -i "./ssh-key-2024-07-04.key"
```


### サンプルアプリの起動
```
streamlit run docsearch.py
```







