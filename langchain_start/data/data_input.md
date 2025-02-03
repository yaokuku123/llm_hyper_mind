# Git本地仓库基本操作

***

## 一. 创建Git项目

* 方法一

在本地的工作目录初始化新仓库，此时Git会自动在当前目录下生成一个隐藏文件 .git 。在该文件里面存放关于Git版本控制相关的配置信息。

```shell
$ git init
```

* 方法二

在远程仓库Github中新建一个项目，并复制新建项目的地址，执行如下操作从远端克隆一份项目，默认就是Git项目，受到Git的控制。

```shell
# git clone [项目地址]
$ git clone https://github.com/yaokuku123/git-remote.git
```

## 二. 提交本地仓库流程

实例：

1. 在当前目录下新建一个文件，并写入内容。执行 git status 命令后，得到如下的结果：

说明：从得到的输出结果可以发现，当我们新建一个文件后，由于没有加入Git的管理，所以此时显示的结果是未跟踪的文件(Untracked files)。

```shell
$ echo "Hello World" > test.txt
$ git status
On branch master
No commits yet
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        test.txt
nothing added to commit but untracked files present (use "git add" to track)
```

2. 将未跟踪的文件变为跟踪文件，并保存至暂存区。执行 git add 命令，得到如下结果：

说明：此时未跟踪的文件已经被Git跟踪，并且加入至暂存区，等待被提交到本地仓库

```shell
$ git add test.txt
$ git status
On branch master
No commits yet
Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   test.txt
```

3. 将暂存区的文件提交到本地仓库，执行 git commit 命令，得到结果如下：

说明：在执行提交命令后，表示已经将该文件纳入Git的本地仓库。再次执行 git status 命令后，可以发现没有其他需要提交的任务。表示此时 工作区，暂存区，本地库 三个位置存储的内容一致

```shell
# -m: 本次提交的说明摘要，若不加 -m ，则会进入vim编辑器，在编辑器的第一行开始写说明摘要
$ git commit -m "create new file test.txt"
$ git status
On branch master
nothing to commit, working tree clean
```

## 三. 提交过程中的撤销命令说明

实例：若按上述的常规操作，则会成功将工作区的文件纳入Git本地库中存储。但在过程中也会出现一些失误或者误操作，故了解提交过程中的撤销命令尤为重要

### 1. 提交到暂存区的文件想要撤回

接着上节的例子，此时我想在test.txt文件中添加一行信息，然后添加到暂存区。执行 git status 命令，发现已经成功添加到暂存区。

```shell
$ echo "Hello Git" >> test.txt
$ cat test.txt
Hello World
Hello Git
$ git add test.txt
$ git status
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   test.txt
```

但此时我发现添加的内容有问题，想将暂存区的内容删除掉。那么此时就有以下几种可以选择的方式

* 方法一：

说明：此方法是通过在工作区修改想要更改的内容，之后重新添加到暂存区。将原先暂存区存储的就内容给覆盖掉。从而达到了删除之前暂存区内容的效果

```shell
$ echo "Hello Git plus" >> test.txt
$ git add test.txt
$ git status
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   test.txt
```

* 方法二：

说明：此方法的原理是使用HEAD指针指向的本地仓库中 test.txt 的文件内容覆盖现在的**暂存区**内容，从而达到了取消暂存文件的效果。通过 git status 命令可以发现已经将暂存区的内容撤销。此方法是**安全**的，不会回滚工作区修改的内容

```shell
$ git reset --mixed HEAD test.txt
$ git status
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   test.txt
no changes added to commit (use "git add" and/or "git commit -a")
$ cat test.txt
Hello World
Hello Git
```

* 方法三：

说明：此方法的原理是使用HEAD指针指向的本地仓库中 test.txt 的文件内容替换掉**暂存区和工作区**的文件。从而达到撤销暂存区内容的目的。但此方法**不安全**，会将工作区的内容全部回滚。通过查看test.txt文件中的内容可以发现之前添加的 Hello Git 内容已经消失

```shell
$ git checkout HEAD test.txt
$ git status
On branch master
nothing to commit, working tree clean
$ cat test.txt
Hello World
```


* 方法四：

说明：此方法的原理是使用HEAD指针指向的本地库中的文件**替换全部**暂存区的文件。从而达到撤销暂存区内容的目的。方法是**安全**的，不会回滚工作区修改的内容

```shell
$ git reset --mixed HEAD
$ git status
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   test.txt
no changes added to commit (use "git add" and/or "git commit -a")
$ cat test.txt
Hello World
Hello Git
```

* 方法五：

说明：此方法的原理是使用HEAD指针指向的本地库中的文件**替换全部**暂存区和工作区的文件。从而达到撤销暂存区内容的目的。但此方法**不安全**，会将工作区的内容全部回滚。通过查看test.txt文件中的内容可以发现之前添加的 Hello Git 内容已经消失。

```shell
$ git reset --hard HEAD
$ git status
On branch master
nothing to commit, working tree clean
$ cat test.txt
Hello World
```

### 2. 提交到本地仓库的文件想要撤回

首先修改文件，将修改后的文件提交到本地仓库中

```shell
$ git add test.txt
$ git commit -m "add one line in test.txt"
```

此时已经成功提交本次修改，但现在发现提交的内容存在问题或者秘密泄露，想要撤回本次的提交，可以如下的方式撤销本次操作

说明：撤销提交到本地参考的操作可以使用 git reset 命令，其中有三个参数可供选择：

* --soft：仅回滚本地仓库的内容，工作区和暂存区的内容不回滚。
* --mixed：(默认) 仅回滚本地仓库和暂存区的内容，工作区的内容不回滚。
* --hard：本地仓库，暂存区，工作区的内容全部回滚。(不安全)

一般选择默认的 --mixed 即可满足需求。另外，HEAD^ 表示当前HEAD指针指向的上一个版本。以此类推 HEAD^^ 表示上两个版本

```shell
$ git reset --soft HEAD^
$ git status
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   test.txt
```

```shell
$ git reset --mixed HEAD^
$ git status
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   test.txt
no changes added to commit (use "git add" and/or "git commit -a")
```

```shell
$ git reset --hard HEAD^
$ git status
On branch master
nothing to commit, working tree clean
```

### 3. 工作区修改的文件想要放弃修改

实例：我对 test.txt 文件中的内容做了修改，将原先的Hello World改为了Hello Coder，然后通过

git status 命令查看发现此时文件处于已修改的状态

```shell
$ echo "Hello Coder" > test.txt
$ git status
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   test.txt
no changes added to commit (use "git add" and/or "git commit -a")
```

若代码或内容改乱了，想要从头开始，丢弃现有的全部修改内容。可以使用如下的方法将工作区重置

* 情形一，若没有添加到暂存区，可以使用该方法

说明：该方法实际上是使用目前状态的**暂存区内容覆盖工作区**的内容，从而实现回滚工作区的效果。由 git status 命令可以看出已经回退了做出的修改

```shell
$ git checkout -- test.txt
$ git status
On branch master
nothing to commit, working tree clean
$ cat test.txt
Hello World
```

* 情形二，若不巧已经添加到暂存区，可以使用该方法。首先回退暂存区，然后回退工作区

说明：由于文件已经提交到暂存区了，所以无法直接使用 git checkout -- [file] 命令回退工作区。这是因为该方法是通过暂存区来覆盖工作区，而现在工作区和暂存区的内容一样了，故无法执行该操作。需要先使用之前介绍的方法回退暂存区的内容，再回退工作区即可

```shell
$ git reset --mixed HEAD test.txt
$ git checkout -- test.txt
$ git status
On branch master
nothing to commit, working tree clean
$ cat test.txt
Hello World
```

* 其他

说明：不管上面何种情形，使用下面的两个方法之一直接暴力回退即可。该命令直接回退到未修改时候的纯净版

```shell
$ git checkout HEAD test.txt
$ git reset --hard HEAD
```

## 四. 分支操作

Git的分支实际上仅仅表示的是指向提交对象的可变指针。每次提交操作都会使其自动向前移动。Git的默认分支为master。

### 1. 分支创建

Git使用如下命令创建分支，该分支会指向当前所在的提交对象

例如：创建一个新分支，名称为dev

```shell
$ git branch dev
```

### 2. 切换分支

可以通过如下命令切换HEAD指针指向新创建的dev分支

```shell
$ git checkout dev
```

### 3. 切换并创建分支

* 情形一，使用如下命令创建并切换分支是安全的，不会涉及到文件的删除或者更新。例如使用下面的命令创建test分支并切换到该分支

```shell
$ git checkout -b test
```

* 情形二，使用如下命令创建并切换到历史中的某个版本，由于该操作会导致当前版本会有文件的删除或者更改，所有会触发Git对该操作的安全检测。需要在工作区，暂存区没有任何更改的前提下，才可以执行。

  例如：创建test分支指向前一个版本，若此时工作区有修改或者暂存区有内容，则会报警告。需要将此次修改提交，或者回滚才可以继续执行该方法

```shell
$ git checkout -b test HEAD^
error: Your local changes to the following files would be overwritten by checkout:
        test.txt
Please commit your changes or stash them before you switch branches.
Aborting
```

## 五. 其他常用操作

### 1. 撤销Git的追踪

说明：新建的文件未受到Git版本控制的追踪，可以使用 git add [file] 命令加入追踪。使用下面的命令可以放弃Git的追踪

```shell
$ git rm --cached test.txt
```

### 2. 删除文件

* 使用git的方法

```shell
$ git rm test.txt
$ git status 
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        deleted:    test.txt
$ git commit -m "delete test.txt"
```

* 使用传统的系统删除命令的方式，与上述使用git的方式区别不大，需要额外增添一步添加到暂存区的命令

```shell
$ rm test.txt
$ git add test.txt
$ git commit -m "delete test.txt"
```

### 3. 修改文件名

* 使用git的方法

```shell
$ git mv test.txt test2.txt
$ git status
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        renamed:    test.txt -> test2.txt
$ git commit -m "renamed test.txt"
```

* 使用传统的系统移动命令的方式，与上述使用git的方式区别不大，需要额外增添一步添加到暂存区的命令。可以发现Git实质上管理采用的方式是将原文件拷贝一份重命名后，删除原文件

```shell
$ mv test.txt test2.txt
$ git status
On branch master
Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        deleted:    test.txt
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        test2.txt
no changes added to commit (use "git add" and/or "git commit -a")
$ git add .
$ git commit -m "renamed test.txt"
```

### 4. 查看日志

每次提交到本地仓库成功均会生成日志，可以通过查看日志了解提交的整个流程链。也可以为之后切换版本，切换分支等操作提供基础

说明：使用 git log 命令查看日志

```shell
# --oneline 仅显示sha1和摘要信息
# --graph 以图像化流程显示，方便之后分支众多的情况下查看日志
# --all 查看所有分支的信息
git log --oneline --graph --all
```

### 5. 跳过暂存区

若本次修改文件后想要直接提交，而不想先到暂存区再提交增加操作步骤的话。可以使用如下命令跳过暂存区。注意：若新创建文件而不是原有文件的修改，则不能跳过暂存区。需要先使用 git add [file] 命令追踪文件，再提交。

```shell
$ git commit -a -m "quick commit"
```