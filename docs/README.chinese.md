# 中文相关 Chinese words tips

```
:%s/，/, /g
:%s/。/. /g

操作完了再反向换回来了就是；注意半角的. 和, 后面跟一个空格。这样w ) ( 都能用一用。

:%s/\. /。/g
:%s/, /，/g
```
 - 略慢凑合用: Chinese words motion plugin for vim: <https://github.com/ZWindL/chword.vim>
 - https://github.com/deton/motion_ja.vim 没跑起来

> 水木vim版上一些人说，不如改造我们的语言，让 每个 词 后面 都 跟 空格 太 激进 了
> 也可以用jieba分词等，提前处理一下srt。
> 反正就是规则，加工的时候用一下，后面直接反过来

