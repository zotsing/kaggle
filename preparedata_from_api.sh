
#!/bin/sh
  
#assign competition name
dir='landmark-retrieval-challenge'

#if dir not exist, download files
if [ ! -d "$dir" ]; then
  kaggle competitions download -c $dir
fi

#unzip files
cd $dir
for f in *.zip
do
  unzip $f
done

#remove zipped file
rm -rf *.zip
