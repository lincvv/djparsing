djparsing 
===========
##### Django application for fast parsing and saving content to the database
Requirements
-----------
* python (3.4, 3.5, 3.6)
* django (1.8, 1.9, 1.10, 1.11)
* lxml (4.1.1)
* cssselect (1.0.1)
* Pillow         

Quick start
-----------
```python
class MyModel(models.Model):
    title = models.CharField(max_length=256)
    text = HTMLField(blank=True)
    source = models.URLField(max_length=255, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True)
    flag = models.BooleanField(default=False)
```
```python
@init(model='Mymodel', app='my_app')
class MyParserClass(Parser):
    body = BodyCSSSelect()
    text = TextContentCssSelect()
    source = AttrCSSSelect(attr_data='href') #Or set the first argument AttrCSSSelect('href')
    title = TextCssSelect()
    img = ImgCSSSelect('src') #The default is src, so the argument is optional. can ImgCSSSelect()
    
pars_obj = MyParserClass(
        body='.content-list__item',
        text='.post__body_crop > .post__text',
        source='a.post__title_link',
        title='a.post__title_link',
        img='.post__body_crop > .post__text img'
        )
pars_obj.run(url='http://site/')
```
    If you need to install an additional field in the database:
```python
pars_obj.data_to_db['flag'] = True
pars_obj.run(url='http://site/')
```

It works on this [site](http://pythoff.com/), all this on the [channel](https://telegram.me/python_all)
