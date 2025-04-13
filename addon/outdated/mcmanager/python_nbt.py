from struct import Struct, error as StructError
from gzip import GzipFile
import warnings


class RestrictedDict(dict):

    def __init__(self, value_validator=None, key_validator=None, iterable=None):
        super().__init__()
        if not value_validator:
            self._validate_value = lambda value: True
        else:
            if not callable(value_validator):
                raise TypeError("value_validator should be a callable or None")
            self._validate_value = value_validator
        if not key_validator:
            self._validate_key = lambda key: True
        else:
            if not callable(key_validator):
                raise TypeError("key_validator should be a callable or None")
            self._validate_key = key_validator
        if iterable:
            self.update(iterable)

    def __setitem__(self, key, value):
        if not self._validate_key(key):
            raise ValueError("Invalid key type, need %s but get %s" % ((t.__name__ for t in self._key_types), type(key)))
        if not self._validate_value(value):
            raise ValueError("Invalid value type, need %s but get %s" % ((t.__name__ for t in self._types), type(value)))
        return super().__setitem__(key, value)

    def can_merge(self, _dict):
        return isinstance(_dict, dict) and all([self._validate_key(k) and self._validate_value(v) for k, v in _dict])

    def trim(self, _dict):
        """
        trim dictionary to fit a form like self
        """
        return {k: v for k, v in _dict if self._validate_key(k) and self._validate_value(v)}

    def update(self, d, trim=False):
        if trim:
            d = self.trim(d)
        if not self.can_merge(d):
            raise ValueError("Cannot update dict because there are invalid keys or values in %s" % str(d))
        return super().update(d)


class TypeRestrictedDict(RestrictedDict):

    def __init__(self, value_types=None, key_types=None, iterable=None):
        """
        @var: acceptable_types: Types that can be a value of this dict
        @var: key_types: Types that can be a key of this dict
        """
        self._types = (tuple(value_types) if not isinstance(value_types, type) else (value_types,)) if value_types else None
        self._key_types = (tuple(key_types) if not isinstance(key_types, type) else (key_types,)) if key_types else None
        super(TypeRestrictedDict, self).__init__(
            key_validator=lambda key: isinstance(key, self._key_types) if self._key_types else True,
            value_validator=lambda value: isinstance(value, self._types) if self._types else True
        )

    @property
    def types(self):
        return self._types

    @property
    def key_types(self):
        return self._key_types


class RestrictedList(list):

    def __init__(self, validator=None, iterable=None, trim=True):
        if validator:
            self._validate = validator
        elif callable(validator):
            self._validate = lambda value: True
        else:
            raise TypeError("Validator must be callable!")
        if iterable:
            self.extend(iterable, trim=trim)

    def append(self, obj):
        if not self._validate(obj):
            raise ValueError("Value %s can not put in this RestrictList" % str(obj))
        return super().append(obj)

    def insert(self, index, obj):
        if not self._validate(obj):
            raise ValueError("Value %s can not put in this RestrictList" % str(obj))
        return super().insert(index, obj)

    def extend(self, iterable, trim=False):
        if not trim:
            cond = map(self._validate, iterable)
            if not all(cond):
                raise ValueError("Contains value that cannot be put into this RestricedList")
        else:
            iterable = [o for o in iterable if self._validate(o)]
        return super().extend(iterable)


class TypeRestrictedList(RestrictedList):

    def __init__(self, types=None):
        self._types = (tuple(types) if not isinstance(types, type) else (types,)) if types else None
        super().__init__(validator=lambda value: isinstance(value, self._types) if self._types else True)

    @property
    def types(self):
        return self._types


class _JavaIntegers:
    _bit_length = 0
    _valid_bits = 0

    def __init__(self, bit_length):
        self._bit_length = bit_length
        self._valid_bits = 0xFF
        for i in range(bit_length // 8 - 1):
            self._valid_bits *= 256
            self._valid_bits += 0xFF

    @property
    def bit_length(self):
        return self._bit_length

    @property
    def max_value(self):
        return 1 << (self.bit_length - 1)

    @property
    def min_value(self):
        return -self.max_value

    @property
    def num_range(self):
        return range(self.min_value, self.max_value)

    @property
    def valid_bits(self):
        return self._valid_bits

    @property
    def sign_bit(self):
        return 1 << (self.bit_length - 1)

    @property
    def number_bits(self):
        return (self.valid_bits + 1) // 2 - 1

    def to_signed(self, v='0', base=10):
        """
        Convert a python int, or objects that can be converted to int,
        into Java type integers.
        This is helful when writing binary file for Java programs to read,
        such as NBT

        For example:
        ```
        >>> from struct import Struct
        >>> int_struct = Struct(">i")
        >>> 0xaccc821c
        2899083804
        >>> JavaInteger(0xaccc821c)
        -1395883492
        >>> int_struct.pack(0xaccc821c)
        Traceback (most recent call last):
          File "<pyshell#15>", line 1, in <module>
            int_struct.pack(0xaccc821c)
        struct.error: argument out of range
        >>> int_struct.pack(JavaInteger.to_signed(0xaccc821c))
        b'\\xac\\xcc\\x82\\x1c'
        ```
        """
        result = int(v, base=base)
        result = result % (self.valid_bits + 1)
        if result not in self.num_range:
            if result & self.sign_bit:
                result -= 1
                result -= self.valid_bits
        return result

    def to_unsigned(self, v='0', base=10):
        """
        Convert a python int, or objects that can be converted to int,
        into Java type integers.
        This is helful when writing binary file for Java programs to read,
        such as NBT

        For example:
        ```
        >>> from struct import Struct
        >>> int_struct = Struct(">i")
        >>> 0xaccc821c
        2899083804
        >>> JavaInteger(0xaccc821c)
        -1395883492
        >>> int_struct.pack(0xaccc821c)
        Traceback (most recent call last):
          File "<pyshell#15>", line 1, in <module>
            int_struct.pack(0xaccc821c)
        struct.error: argument out of range
        >>> int_struct.pack(JavaInteger.to_unsigned(0xaccc821c))
        b'\\xac\\xcc\\x82\\x1c'
        ```
        """
        result = int(v, base=base)
        result = result % (self.valid_bits + 1)
        if result not in self.num_range:
            if result < 0:
                result += 1
                result += self.valid_bits
        return result

    def validate(self, v):
        return isinstance(v, int) and v in self.num_range


JavaByte = _JavaIntegers(8)
JavaShort = _JavaIntegers(16)
JavaInteger = _JavaIntegers(32)
JavaLong = _JavaIntegers(64)

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

TAGLIST = {}


class NBTTagBase:
    _type_id = None

    def __init__(self, value=None, **kwargs):
        """
        Don't use this
        This is just for code reuse
        """
        if hasattr(value, 'read'):
            self._read_buffer(value)
        elif hasattr(kwargs.get('buffer', None), 'read'):
            self._read_buffer(kwargs.get('buffer'))
        else:
            self._value = value

    def _write_buffer(self, buffer):
        pass

    def _read_buffer(self, buffer):
        pass

    @property
    def type_id(self):
        return self._type_id

    @property
    def value(self):
        return self._value

    def _value_json_obj(self, full_json=True):
        return self.value

    def json_obj(self, full_json=True):
        """
        Return json format object of this NBT tag.
        full_json is True by default, which indicates it will export json with this tag's type id
            set to False to get a cleaner json object
        """
        if full_json:
            return {"type_id": self.type_id, "value": self._value_json_obj(full_json)}
        else:
            return self._value_json_obj(full_json)

    def __str__(self):
        return str(self.json_obj())

    def __repr__(self):
        return self.json_obj().__repr__()

    def _value_from_json(self, json_value):
        pass

    def __eq__(self, value):
        return (self.type_id == getattr(value, 'type_id', None) and self.value == getattr(value, 'value', None)) or self.value == value

    def __init_subclass__(cls):
        if cls._type_id is not None:
            if cls._type_id not in TAGLIST.keys():
                # If a subclass doesn't have _type_id, don't add it into TAGLIST
                # Prevent Overriding TAGLIST when user subclassing
                # Still available for adding items int TAGLIST
                TAGLIST[cls._type_id] = cls


class NBTTagEnd(NBTTagBase):
    """
    This is just for File I/O
    """

    _type_id = TAG_END
    fmt = Struct(">b")

    def __init__(self):
        super().__init__()

    def _read_buffer(self, buffer):
        value = self.fmt.unpack(buffer.read(1))[0]
        if value != 0:
            raise ValueError(
                "A Tag End must be rendered as '0', not as '%d'." % value
            )

    def _write_buffer(self, buffer):
        buffer.write(b'\x00')


class NBTTagSingleValue(NBTTagBase):
    """
    Just for code reuse
    """

    fmt = None

    def __init__(self, value=None, **kwargs):
        if value:
            if not self._validate(value):
                raise ValueError("Invalide value %s for class %s." % (value, self.__class__.__name__))
        super().__init__(value=value, **kwargs)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if not self._validate(v):
            raise ValueError("Cannot apply value %s to %s" % (v, self.__class__.__name__))
        self._value = v

    def _validate(self, v):
        return True

    def _read_buffer(self, buffer):
        self.value = self.fmt.unpack(buffer.read(self.fmt.size))[0]

    def _write_buffer(self, buffer):
        buffer.write(self.fmt.pack(self.value))

    def _value_json_obj(self, full_json=True):
        return self.value

    def _value_from_json(self, json_obj):
        self.value = json_obj['value']


class NBTTagContainerList(NBTTagBase, RestrictedList):
    """
    Just for code reuse and better interfaces
    """

    def __init__(self, value, **kwargs):

        # Leave self._validate unfilled
        # This should be filled by subclasses ahead of calling this initializer
        # If unfilled, self._validate should be filled as default set in RestrictedList
        if not self._validate:
            RestrictedList.__init__()

        __buffer = None
        if hasattr(kwargs.get('buffer', None), 'read'):
            __buffer = kwargs.get('buffer')
        elif hasattr(value, 'read'):
            __buffer = value
        elif hasattr(value, '__iter__'):
            self.extend(value, trim=False)
        else:
            pass
            # Do nothing

        if __buffer:
            self._read_buffer(__buffer)

    @property
    def value(self):
        return self[:]


# == Actual NBT tag types from here ==

class NBTTagByte(NBTTagSingleValue):
    _type_id = TAG_BYTE
    fmt = Struct(">b")

    def __init__(self, value=0, **kwargs):
        super().__init__(value=value, **kwargs)

    def _validate(self, v):
        return JavaByte.validate(v)


class NBTTagShort(NBTTagSingleValue):
    _type_id = TAG_SHORT
    fmt = Struct(">h")

    def __init__(self, value=0, **kwargs):
        super().__init__(value=value, **kwargs)

    def _validate(self, v):
        return JavaShort.validate(v)


class NBTTagInt(NBTTagSingleValue):
    _type_id = TAG_INT
    fmt = Struct(">i")

    def __init__(self, value=0, **kwargs):
        super().__init__(value=value, **kwargs)

    def _validate(self, v):
        return JavaInteger.validate(v)


class NBTTagLong(NBTTagSingleValue):
    _type_id = TAG_LONG
    fmt = Struct(">q")

    def __init__(self, value=0, **kwargs):
        super().__init__(value=value, **kwargs)

    def _validate(self, v):
        return JavaLong.validate(v)


class NBTTagFloat(NBTTagSingleValue):
    _type_id = TAG_FLOAT
    fmt = Struct(">zb")

    def __init__(self, value=.0, **kwargs):
        super().__init__(value=value, **kwargs)

    def _validate(self, v):
        return isinstance(v, (int, float))


class NBTTagDouble(NBTTagSingleValue):
    _type_id = TAG_DOUBLE
    fmt = Struct(">d")

    def __init__(self, value=.0, **kwargs):
        super().__init__(value=value, **kwargs)

    def _validate(self, v):
        return isinstance(v, (int, float))


class NBTTagString(NBTTagSingleValue):
    _type_id = TAG_STRING

    def __init__(self, value="", **kwargs):
        super().__init__(value=value, **kwargs)

    def _validate(self, v):
        return isinstance(v, str) and len(v) < 0x8000

    def _read_buffer(self, buffer):
        length = NBTTagShort(buffer=buffer).value
        s = buffer.read(length)
        if len(s) != length:
            raise StructError()
        self.value = s.decode("utf-8")

    def _write_buffer(self, buffer):
        byte_code = self.value.encode("utf-8")
        length = NBTTagShort(len(byte_code))
        length._write_buffer(buffer)
        buffer.write(byte_code)


class NBTTagByteArray(NBTTagContainerList):
    _type_id = TAG_BYTE_ARRAY

    def __init__(self, value=None, **kwargs):
        self._validate = JavaByte.validate
        super().__init__(value=value, **kwargs)

    def _read_buffer(self, buffer):
        length = NBTTagInt(buffer=buffer).value
        self.extend(list(bytearray(buffer.read(length))))

    def _write_buffer(self, buffer):
        length = NBTTagInt(len(self.value))
        length._write_buffer(buffer)
        buffer.write(bytes(self.value))

    def _value_from_json(self, json_obj):
        self.clear()
        self.extend(json_obj['value'])


class NBTTagIntArray(NBTTagContainerList):
    _type_id = TAG_INT_ARRAY

    def __init__(self, value=None, **kwargs):
        self._validate = JavaInteger.validate
        super().__init__(value=value, **kwargs)

    def _read_buffer(self, buffer):
        length = NBTTagInt(buffer=buffer).value
        fmt = Struct(">" + str(length) + "i")
        self.clear()
        self.extend(list(fmt.unpack(buffer.read(fmt.size))))

    def _write_buffer(self, buffer):
        length = len(self.value)
        fmt = Struct(">" + str(length) + "i")
        NBTTagInt(length)._write_buffer(buffer)
        buffer.write(fmt.pack(*self.value))

    def _value_from_json(self, json_obj):
        self.clear()
        self.extend(json_obj['value'])


class NBTTagLongArray(NBTTagContainerList):
    _type_id = TAG_LONG_ARRAY

    def __init__(self, value=None, **kwargs):
        self._validate = JavaLong.validate
        super().__init__(value=value, **kwargs)

    def _read_buffer(self, buffer):
        length = NBTTagInt(buffer=buffer).value
        fmt = Struct(">" + str(length) + "q")
        self.clear()
        self.extend(list(fmt.unpack(buffer.read(fmt.size))))

    def _write_buffer(self, buffer):
        length = len(self.value)
        fmt = Struct(">" + str(length) + "q")
        NBTTagInt(length)._write_buffer(buffer)
        buffer.write(fmt.pack(*self.value))

    def _value_from_json(self, json_obj):
        self.clear()
        self.extend(json_obj['value'])


class NBTTagList(NBTTagContainerList):
    _type_id = TAG_LIST

    def __init__(self, value=None, **kwargs):
        """
        If you are creating a NBTTagList yourself,
        Please specify a tag_type (must be a subclass of NBTTagBase)
        """
        tag_type = kwargs.get('tag_type', None)
        if tag_type:
            self._tag_type_id = tag_type._type_id
        else:
            self._tag_type_id = None
        self._validate = lambda v: isinstance(v, self.tag_type)
        super().__init__(value=value, **kwargs)

    @property
    def tag_type_id(self):
        return self._tag_type_id

    @property
    def tag_type(self):
        return TAGLIST.get(self._tag_type_id, NBTTagBase)

    def _read_buffer(self, buffer):
        self._tag_type_id = NBTTagByte(buffer=buffer).value
        self.clear()
        length = NBTTagInt(buffer=buffer).value
        for i in range(length):
            self.append(TAGLIST[self._tag_type_id](buffer=buffer))

    def _write_buffer(self, buffer):
        if self.tag_type_id == None:
            raise ValueError("No type specified for NBTTagList: %s" % self.json_obj())
        NBTTagByte(self.tag_type_id)._write_buffer(buffer)
        length = NBTTagInt(len(self))
        length._write_buffer(buffer)
        for i, tag in enumerate(self.value):
            if tag.type_id != self.tag_type_id:
                raise ValueError(
                    "List element %d(%s) has type %d != container type %d" %
                    (i, tag, tag.type_id, self.tag_type_id))
            tag._write_buffer(buffer)

    def _value_json_obj(self, full_json=True):
        return [tag._value_json_obj(full_json) for tag in self.value]

    def json_obj(self, full_json=True):
        """
        Add tag type id into result 
        """
        r = super().json_obj(full_json=full_json)
        if full_json:
            r['tag_type_id'] = self.tag_type_id
        return r

    def _value_from_json(self, json_obj):
        self.clear()
        self._tag_type_id = json_obj['tag_type_id']
        self.extend([self.tag_type(v) for v in json_obj['value']])


class NBTTagCompound(NBTTagBase, TypeRestrictedDict):
    _type_id = TAG_COMPOUND

    def _read_buffer(self, buffer):
        while True:
            _type = NBTTagByte(buffer=buffer).value
            if _type == TAG_END:
                break
            else:
                name = NBTTagString(buffer=buffer).value
                if not _type in TAGLIST.keys():
                    raise ValueError("Unrecognized tag type %d" % _type)
                tag = TAGLIST[_type](buffer=buffer)
                self[name] = tag

    def _write_buffer(self, buffer):
        for key, tag in self.items():
            NBTTagByte(value=tag.type_id)._write_buffer(buffer)
            NBTTagString(value=key)._write_buffer(buffer)
            tag._write_buffer(buffer)
        NBTTagEnd()._write_buffer(buffer)

    def _value_json_obj(self, full_json=True):
        result = {}
        for key, value in self.items():
            result[key] = value.json_obj(full_json=full_json)
        return result

    def _value_from_json(self, json_obj):
        for k, v in json_obj['value'].items():
            self[k] = from_json(v)

    @property
    def value(self):
        return self

    def __eq__(self, value):
        return all([value.get(k, None) == v for k, v in self.items()])

    def setTag(self, key, value):
        self[key] = value

    def __init__(self, value=None, **kwargs):
        TypeRestrictedDict.__init__(self, value_types=NBTTagBase, key_types=str)
        __buffer = kwargs.get('buffer', None) if hasattr(kwargs.get('buffer', None), 'read') else value
        if hasattr(__buffer, 'read'):  # If there is a buffer, read from it
            self._read_buffer(__buffer)
        elif isinstance(value, dict):  # Copy an NBTTagCompound, or something alike, if no buffer available
            self.update(value)
        elif value:  # Other values are illegal
            raise ValueError('Illegal value %s for %s!' % (value, self.__class__.__name__))
        else:  # Generate an empty TagCompound
            pass

        # Add type specified getter and setters
        def _setTagWithType(_type):
            def setter(self, key, value):
                if not isinstance(value, _type):  # If not an NBT object for the specified type, convert it to one
                    self[key] = _type(value)
                else:  # If it already is, just add.
                    self[key] = value

            return setter

        def _getTagWithType(_type):
            def getter(self, key):
                return self.get(key, _type()).value

            return getter

        import types
        for cls in TAGLIST.values():
            # Since TAGLIST was completly filled when subclass-ing
            # And self.__init__ will be called when instanciating
            # Add type-specified methods here shall not raise Error
            name = cls.__name__[3:]
            setattr(self, 'set' + name, types.MethodType(_setTagWithType(cls), self))
            setattr(self, 'get' + name, types.MethodType(_getTagWithType(cls), self))


# Map Minecraft Wiki names to class names
# For compatibility
TAG = NBTTagBase
TAG_Byte = NBTTagByte
TAG_Short = NBTTagShort
TAG_Int = NBTTagInt
TAG_Long = NBTTagLong
TAG_Float = NBTTagFloat
TAG_Double = NBTTagDouble
TAG_Byte_Array = NBTTagByteArray
TAG_Int_Array = NBTTagIntArray
TAG_Long_Array = NBTTagLongArray
TAG_String = NBTTagString
TAG_List = NBTTagList
TAG_Compound = NBTTagCompound
TAG_End = NBTTagEnd

# Also:
# =============================

TagBase = NBTTagBase
TagByte = NBTTagByte
TagShort = NBTTagShort
TagInt = NBTTagInt
TagLong = NBTTagLong
TagFloat = NBTTagFloat
TagDouble = NBTTagDouble
TagByteArray = NBTTagByteArray
TagIntArray = NBTTagIntArray
TagLongArray = NBTTagLongArray
TagString = NBTTagString
TagList = NBTTagList
TagCompound = NBTTagCompound
TagEnd = NBTTagEnd


# =============================

def read_from_nbt_file(file):
    """
    Read NBTTagCompound from a NBT file
    """
    _file = GzipFile(file, "rb") if isinstance(file, str) else GzipFile(fileobj=file, mode="rb")
    _type = NBTTagByte(buffer=_file).value
    _name = NBTTagString(buffer=_file).value
    return TAGLIST[_type](buffer=_file)


def write_to_nbt_file(file, tag: NBTTagCompound, name=''):
    """
    Write a NBTTagCompound to a NBT file
    name affects nothing currently
    """
    _file = GzipFile(file, "wb") if isinstance(file, str) else GzipFile(fileobj=file, mode="wb")
    NBTTagByte(tag.type_id)._write_buffer(_file)
    NBTTagString(name)._write_buffer(_file)
    tag._write_buffer(_file)


def from_json(json_obj):
    type_id = json_obj['type_id']
    if type_id not in TAGLIST.keys():
        raise ValueError("Unrecognized tag type %d" % type.value)
    tag = TAGLIST[type_id]()
    tag._value_from_json(json_obj)
    return tag
