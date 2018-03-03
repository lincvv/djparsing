djparsing 
===========
##### Django application for fast parsing and saving content to the database
parser of the first data block (by date this is new) and saving in the specified table

Requirements
-----------
* python (3.4, 3.5, 3.6)
* django (1.8, 1.9, 1.10, 1.11)
* lxml (4.1.1)
* cssselect (1.0.1)
* Pillow         

Quick start
-----------
##### Install:
        pip install djparsing
##### Using:
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
from djparsing.core import Parser, init
from djparsing import data

@init(model='MyModel', app='my_app')
class MyParserClass(Parser):
    body = data.BodyCSSSelect()
    text = data.TextContentCSSSelect()
    source = data.AttrCSSSelect(attr_data='href') #Or set the first argument AttrCSSSelect('href')
    title = data.TextCSSSelect()
    img = data.ImgCSSSelect('src') #The default is src, so the argument is optional. can ImgCSSSelect()
    
    class Meta:
        coincidence = ['Python', 'Django', 'Питон', 'ML'] # a list of words for the condition that the data fit
        field_coincidence = 'title' # field to which a list of words is used
    
pars_obj = MyParserClass(
        body='.content-list__item',
        text='.post__body_crop > .post__text',
        source='a.post__title_link',
        title='a.post__title_link',
        img='.post__body_crop > .post__text img',
        url='http://site/'
        )
pars_obj.run()
```
Note: a model for saving data can be specified in Meta class

```python
class Meta:
    model = MyModel # decorator @init is not needed
```
Inheritance:
```python
class MyChildParserClass(MyParserClass):
    my_field = data.TextCSSSelect()
```
Note: fields from the base class, and also the Meta class is inherited. You can override
    
If you need to install an additional field in the database:
```python
pars_obj.add_field['flag'] = True
pars_obj.run()  #if you do not need to save to the database and print the data to the log, 
                # add the argument log -> run(log=True) and redefine the method log_output(self, result):
```
    Example:
```python
@init(model='MyModel', app='my_app')
class MyParserClass(Parser):
    body = data.BodyCSSSelect()
    text = data.TextContentCSSSelect()
    
    def log_output(self, result): # if you do not override the method, the result will be output to the terminal
        pass # and work further with the result
```
Attributs
=========
##### start_url

```python
# initialize the path to the URL with the data block.
# This is needed when the list of objects is on the page, and the data is on another page 
BodyCSSSelect(start_url='div.description.float-right > a')
```
Note: in the attribute with the URL should be href

##### add_domain
```python
# if the URL in the attribute does not have a domain
# set add_domain=True, by default False

BodyCSSSelect(start_url='div.description.float-right > a', add_domain=True)
```

##### save_start_url
when you need to save additional data in the field, 
such as the start URLs of objects, add the ExtraDataField field (save_start_url = True)

##### body_count
how many objects are parsing

    Example:
```python
class MyParserClass(Parser):
    start = BodyCssSelect(start_url='ul.quest-tiles > li.quest-tile-1 > div.item-box > div.item-box-desc h4  a',
                          add_domain=True,
                          body_count=4)
    source = ExtraDataField(save_start_url=True)

```
It works on this [site](http://pythoff.com/), all this on the [channel](https://telegram.me/python_all)
-----