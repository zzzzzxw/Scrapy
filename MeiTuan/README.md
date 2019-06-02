根据网上大神破解的token,伪造token
token分析：
sign值=areaId=40&cateId=0&cityName=重庆&dinnerCountAttrId=&optimusCode=1&
  originUrl=https://cq.meituan.com/meishi/&page=1&partner=126&platform=1&riskLevel=1&sort=&
  userId=&uuid=780104cb5af24160b2c9.1558924082.1.0.0
可以看到解压后是请求的参数信息，采用token相同的加密方式，即先压缩再进行base644编码得到
固定参数 = {"rId":100900,"ver":"1.0.6","ts":1558959462020,"cts":1558959462101,"brVD":[1688,192],"brR":[[1920,1080],[1920,1040],24,24],
  "bI":["https://cq.meituan.com/meishi/","https://cq.meituan.com/"],"mT":[],"kT":[],"aT":[],"tT":[],"aM":"","sign":加密后的sign值}

参数大多都是一些无用的值或者是不会检验的值，例如brVD，brR是登录环境，分辨率等，ts和cts要注意一下，ts是1970至今的的秒数，cts经过测试大约等于
ts加上90~120之间的值

token值 = 固定参数先压缩再base64编码
其中sign的值是随着地区和页面的变化而偏移的，一个uuid的值可以使用一段时间，只需要遍历areaId和pg就可以获取到全部

还需要注意的是，在拿到返回的json格式数据过后，提取出店铺的id进行店铺详情页面请求的时候，需要带上完整的cookie，我没有测试多久会封掉一个cookie，
但是同一个cookie是有频率限制的，并且评论这些内容又是藏在js里面的，但好在可以直接提取到店铺的电话和营业时间，这些数据加上之前json里面的数据已经
足够了。我自己尝试的一个方法，通过免费的ip用selenium去访问网站，等待页面完全加载然后提取cookie，判断cookie是否完整，完整则保存，网上的ip大多都
不好使了，所以有闲心的可以去买点ip来大规模的获取。

后续继续更新对美团的地区的分析
