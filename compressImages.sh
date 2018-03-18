for var in "$@"
do
    jpegoptim --size=400k "$var"
done
