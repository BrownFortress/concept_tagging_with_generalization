for dir in results/*;
do

  for file in $dir/*;
  do
    echo -e "\033[1;32m${dir}${file}\033[0m"
    echo "\n"
    perl ./conlleval.pl < $file 
  done
done
