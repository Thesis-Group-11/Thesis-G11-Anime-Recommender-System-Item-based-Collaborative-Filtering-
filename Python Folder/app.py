#Flask Integration
from flask import Flask, request, jsonify

app = Flask(__name__)
#Packages
import pandas as pd
import numpy as np
import scipy as sp
import pickle
import operator
#Dataframes

synopsis = pickle.load(open('synopsis_df(101622).pkl', 'rb'))
synopsis_df = pd.DataFrame(synopsis)


item_sim = pickle.load(open('item_sim_df(102422).pkl', 'rb'))
item_sim_df = pd.DataFrame(item_sim)



#Functions for Getting MetaData6
@app.route('/GetAnimeFrame/<anime>')
def GetAnimeFrame(anime = None): 
  if isinstance(anime, int):
    return synopsis_df[synopsis_df.anime_id == anime]
  if isinstance(anime, str):
    if anime.islower() == True:
      return synopsis_df[synopsis_df.lowered == anime]
    else:
      return synopsis_df[synopsis_df.Name == anime]


@app.route('/rec', methods = ['GET'])
def rec_all():
  anime_list = request.args.getlist('anime')
  totalrecommendations = []
  #Top 10 recs will be sorted out for display
  recs = [[], [], [], [], [], [], [], [], [], [],]
  
  for anime in anime_list:
    final_list = []
    frame = GetAnimeFrame(anime.lower())
    anime_name = frame.Name.values[0] #Use the Name to get Similar Animes
    
    for item in item_sim_df.sort_values(by = anime_name, ascending = False).index[1:11]: #index[1:6] it starts in 1 so that it wont recommend itself, and 6 so that it prints animes in the index from 1-6
      #Gets the metadata of each anime and then put them in a dictionary which will be appended to a list so that it can be converted into a json file
      frame = GetAnimeFrame(item)
      anime_id = frame.anime_id.values[0]
      Name =  frame.Name.values[0]
      en_name = frame.EN_Name.values[0]
      genre = frame.Genres.values[0]
      synopsis = frame.synopsis.values[0]
      imgurl = frame.imgurl.values[0]
      final_list.append({
                 'anime_id': int(anime_id),
                 'Name': str(Name),
                 'EN_Name': str(en_name),
                 'Genres': str(genre),
                 'Similarity': item_sim_df.at[str(Name), anime_name],
                 'synopsis':str(synopsis),
                 'imgurl': str(imgurl)
                 })
    
    for i in range(len(final_list)):
      recs[i].append(final_list[i])
  
  #Sort the recommendations based on their positioning
  for sorted in recs:
    for anime in sorted:
      if anime not in totalrecommendations and anime['Name'] not in anime_list:
        totalrecommendations.append(anime)

  print('Total recommendations: ', len(totalrecommendations))
  #Sorts the recomemndations based on their similarity Value
  totalrecommendations.sort(key=operator.itemgetter('Similarity'), reverse= True)
  return jsonify(totalrecommendations)

if __name__ == '__main__':
    app.run()
