# gpt2_stor

## How to use

This API has 2 versions available

**first : long**  
text : begining of the text you want to generate  
number_samples : the number of sentence that will be generated  
length : the length of each sentence  

**In CLI condition** :
curl --location --request POST 'https://main-gpt2-story-gmlee329.endpoint.ainize.ai/gpt2-story/long' --form 'text=once upon a time' --form 'num_samples=5' --form 'length=10'

**second : short**  
text : begining of the text you want to generate  
number_samples : the number of word that will be generated  

**In CLI condition** :
curl --location --request POST 'https://main-gpt2-story-gmlee329.endpoint.ainize.ai/gpt2-story/short' --form 'text=once upon a time' --form 'num_samples=5'
