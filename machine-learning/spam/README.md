
This is a simple spam filter using Naïve Bayes for classification. To
try it out, download [the SpamAssassin public
corpus](http://spamassassin.apache.org/publiccorpus/).

Run the classifier like this:

  python ham-dir spam-dir file1 file2 file3 ...

It will train itself on emails from the ham and spam directories, then
attempt to classify the files one by one.