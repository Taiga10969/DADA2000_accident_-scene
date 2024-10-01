<h1 align="center">DADA2000_accident_scene</h1>
<!--p align="center">hogehoge</p-->
DADA2000_accident_sceneは，事故の場面を含む動画で構成されているDADA2000データセットをベースとして，その動画内の実際に事故が起きているフレーム画像を集めたものである．<br>
実際に事故が起きているフレーム画像は，人間によるアノテーションにより抽出されたものである．このレポジトリでは，人間によるアノテーションツールを提供する．

## 環境構築 / データセットの用意
以下のようにして，必要なパッケージをインストールする．
```
pip install -r requirements.txt
```
DADA2000データセットをベースとするため，DADA2000からデータセットを取得する．<br>
データセットはここを参考に取得・処理する．処理により生成された動画像データ`/videos`を`./dataset/videos`に配置する．<br>
ここで処理された画像は`.avi`形式で保存されており，扱うことが困難であるため以下のようにして`.mp4`への変換を行う．
```
bash scripts/convert_avi2mp4.sh
```
この実行では，1枚あたり10s程処理に時間がかかり，データセット全てに適応すると約3時間程度必要である．

## アノテーションツール (streamlit app)
アノテーションツール (streamlit app)を以下ようにして起動する．<br>
一番上の動画が表示されている部分は，全体の動画を確認するために使用し，スライドバー部分で事故場面のフレームを選択する．<br>
さらに，簡単にどんな場面かを選択し，最終的に[確定]ボタンを押して次の動画へと進む．<br>
この実装では，途中で終了しても再実行時に`./annotation/log.csv`を参照することで途中から再開可能である．
```
cd app
streamlit run annotation_app.py
```
この実行より表示されるURLにアクセスすることで，webアプリケーションとしてアノテーションツールを起動可能．<br>
▼streamlit実行結果

### アノテーション基準
- **フレーム選択基準**<br>
  アノテーションにより選択したフレームでどんな事故であるかの説明を行うことができることを理想とする．
  そのため事故の瞬間（ex:車と人が接触した瞬間）を選択するのではなく，**その数フレーム前の可能な限りブレ(ぼやけ)が少ないフレームを選択する**こととする．
  これにより，事故の内容（ex:車と車の間からの飛び出し）を1フレームで確認できる．
- **事故タイプの選択基準**<br>
  `car-to-car`：車と車の事故<br>
  `car-to-pedestrian`：車と歩行者との事故<br>
  `car-to-bicycle`：車と自転車との事故<br>
  `ather`：その他<br>
  `bad`：その他，動画として成立していない / 除外したほうが良い<br>
