# NewsClassification

## Usage
To crawl the news from ETtoday:
```pythonning_folder] -E [test_folder]
```
- `training_folder`    : Folder name for training news.  
- `test_folder`   : Folder name for testing news.

## Required packages:
```
requests
beautifulsoup4
urllib
python ETtodayCrawler.py -F [folder_name] -N [number]
```
- `folder_name`    : Folder name for creating folder to reposit news.
- `number`   : Number of news for each catogory.


To train and test the model of SVM with different parameters:
```python
python SVMTrainer.py -T [trai
jieba
numpy
pandas
sklearn
```

## Categories of news collected:
```
politics - 政治
finance - 財經
entertainment - 影劇
sports - 運動
society - 社會
local - 地方
world - 國際,大陸
lifestyle - 消費,生活
health - 健康
travel - 旅遊
odd - 新奇,寵物
```
> The contents of news are got rid of ads, dates, reporters, figures (but keep captions)ten