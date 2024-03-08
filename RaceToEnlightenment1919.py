#Installation and importing

#Requirments 
#pip install pyspark tk pyvis networkx bs4 requests

import requests
from bs4 import BeautifulSoup
import re
import sys
import numpy as np
import networkx as nx
from pyvis.network import Network
import tkinter as tk
from tkinter.filedialog import asksaveasfile
import cProfile

bgcolour = "#171e29"
fgcolour = "#32d9d0"

app = tk.Tk()
app.title("Race to Enlightenment")
app.configure(bg = bgcolour)

numberOfTopics = []
resultsDisplay = []
resultsVar = tk.StringVar(app, "")
edgesVar = tk.StringVar(app, "")

"""#Functions"""

def getTextBetweenBrackets(text):
  #regex will filter out nested parantheses in format (()) but not (()()) so two searches are used
  res1 = re.findall(r'\([^()]*\)', text)
  text = re.sub(r'\([^()]*\)', '', text)
  res2 = re.findall(r'\([^()]*\)', text)
  res = res1+res2
  return res

def getHTML(URL):
  response = requests.get(URL)
  soup = BeautifulSoup(response.content, 'html.parser')
  if response == "<Response [404]>":
    return 0
  else:
    return soup

##IMplement check if Paragraphs in soup 
def getParagraphs(soup):
  paragraph = list()
  for table in soup.find_all("table"):
    table.decompose()
  paragraph = soup.find_all("p",{"style": False, "class":False})
  return paragraph

def getTopicFromRandom():
    thisArticle ="https://en.wikipedia.org/wiki/Special:Random"
    soup = getHTML(thisArticle)
    header = soup.find("title").get_text()
    topic = header.replace(' - Wikipedia', '')
    return topic

def getLink(paragraphs):
  for paragraph in paragraphs:
      if paragraph is not None:
        links = paragraph.find_all("a",{"title":True})
        paragraphText = paragraph.getText()
        textBetweenBrackets = getTextBetweenBrackets(paragraphText)
        for link in links:
          if not [i for i in textBetweenBrackets if link.getText() in i]:
            if 'page does not exist' not in link.get('title'):
                return link
      else:
          return None        

def newArticle(link):
  WikiURL = "https://en.wikipedia.org/"
  link = link["href"]
  if str(link)[1]== "w":
    newLink = WikiURL + link
    return newLink

def createEdges(topic):
  topic = topic.replace('&','%27')
  thisArticle = "https://en.wikipedia.org/wiki/" + topic
  soup = getHTML(thisArticle)
  
  tempArticles = []
  originalTopic = topic
  iterations = 0
       
  while topic != 'philosophy':
    iterations+=1
    #If you have hit a loop
    if topic in tempArticles:
      edgesVar.set(edgesVar.get() + str(tempArticles))
      resultsVar.set(resultsVar.get()+"-1,")      
      break

    if soup.find('title') != None:
      #if you have hit a search results page
      if 'Search results' in soup.find('title').getText():
        edgesVar.set(edgesVar.get() + str(tempArticles))
        resultsVar.set(resultsVar.get()+"-2,") 
        break

    paragraphs = getParagraphs(soup)
    link = getLink(paragraphs)
    
    #if you have hit a page of only links
    if link is None:
        edgesVar.set(edgesVar.get() + str(tempArticles))
        resultsVar.set(resultsVar.get()+"-3,") 
        break
    
    tempArticles.append(topic)
    topic = link.getText()
    thisArticle = newArticle(link)
    soup = getHTML(thisArticle)
    
  tempArticles.append('Philosophy,')
  resultsVar.set(resultsVar.get()+str(iterations)+",") 
  edgesVar.set(edgesVar.get() + str(tempArticles))


def displayResults(results):
    index = 0
    for result in results:
        if int(result) > 0:
            result = "has reached enlightenment in "+str(result)+" steps"
        elif int(result) == 0:
            result = "dont try to be too clever"
        else:
            result = " has gotten lost on the path to enlightenment"
        entry = tk.Entry(app, bg = bgcolour, fg = fgcolour, width = 50)    
        entry.grid(column=2,row=index+1,sticky=tk.N+tk.E+tk.S+tk.W)
        entry.insert(tk.END, result)
        resultsDisplay.append(entry)
        index = index+1
        
"""#Running"""

def race():
    edgesVar.set("")
    resultsVar.set("")
    topics = list()
    
    topics =  [entry.get() for entry in numberOfTopics]
    
    list(map(createEdges, topics))

    results = resultsVar.get()
    results = results[:-1].split(",")
    print(results)
    displayResults(results)
    
"""#Graphing"""

def reshape(articles):
  size = len(articles)
  #Converts list to list of lists based on value of "philosophy" in list 
  #This allows the graph to be generated and displayed correctly 
  idx_list=[idx +1 for (idx, val) in enumerate(articles) if val == ' Philosophy']
  res = [articles[i:j] for i, j in zip([0] + idx_list, idx_list+([size] if idx_list[-1] != size else[]))]
  return res

def graph():
    edges = edgesVar.get()
    edges = edges[1:-1]
    edges = re.sub(r'[\']*|[\"]*|[\[]|[\]]*', '', edges)

    edges = edges.split(",")
    #Split adds " around existing ' attempt to remove this to properly use idx list in reshape()
    edges = reshape(edges)

    if edges:  
        edgesFinal = np.empty((2,0))  
        G = nx.Graph(Notebook = True)
        for i in edges:
          sources = i[:-1]
          targets = i[1:]
          tempEdges = np.stack((sources, targets), axis=1)
          G.add_edges_from(tempEdges)
        net = Network()
        graphFile = net.from_nx(G)
        #printsHTML can add this to file as text like normal and save 
        c = net.generate_html()
        f = asksaveasfile(initialfile = 'RaceToEnlightenment',defaultextension=".html",filetypes=[('All Files', '*.*'),("Hyper Text Markup Language Files","*.html")])
        f.write(c)   
        f.close()
    else:
        print("failed to create graph")

def add_input_fields(num_fields):
    numberOfTopics.clear()
    for topicEntry in range(num_fields):
        # Create an Entry widget for user input and store it in the list
        entry = tk.Entry(app, bg = bgcolour, fg = fgcolour, width = 50 )
        entry.grid(column=0,row=topicEntry+1,columnspan=2, sticky=tk.N+tk.E+tk.S+tk.W)
        topic = getTopicFromRandom()
        entry.insert(0, topic)
        numberOfTopics.append(entry)  # Store the Entry widget in the list

# Entry widget for the user to input the number of fields
def getTopics():
   for i in numberOfTopics:
       i.destroy()
   for i in resultsDisplay:
       i.destroy()

   resultsDisplay.clear()

   try:
      num_fields = int(num_fields_entry.get())
      add_input_fields(num_fields)
   except ValueError:
      # Display an error message if the user input is not a valid number
      tk.messagebox.showerror("Error", "Please enter a valid number.")
      
"""# GUI"""
      
num_fields_entry = tk.Entry(app, bg = bgcolour, fg = fgcolour)
num_fields_entry.grid(column=0,row=0)
num_fields_entry.insert(0,'2')
    
addTopicsButton = tk.Button(app, text="Add Topics", command=getTopics, bg = bgcolour, fg = fgcolour)
addTopicsButton.grid(column=1,row=0)

startRaceButton = tk.Button(app, text="Start Race", command=race, bg = bgcolour, fg = fgcolour)
startRaceButton.grid(column=5,row=11, sticky=tk.E )

rules = tk.Text(app, bg = bgcolour, fg = fgcolour)
rules.insert(tk.END, "Instructions \n 1. Pick the number of topics you would to race \n 2. Press \"Add Topics\"\n 3.If you would like to change any topics you can do so \n 4. Press \"Start Race\" \n 5. The lowest number of steps wins\n 6. If you would like to save a graph of the race press \"Save Graph\"")
rules.insert(tk.END,"\n\nProposed Drinking game \nWinner (lowest number of steps) is safe\nLosers have to take a drink\nIf you get lost on the path to enlightenment finish your drink")
rules.grid(column = 5, row = 0, columnspan= 3, rowspan= 10)

saveGraphButton = tk.Button(app, text="SaveGraph", command=graph, bg = bgcolour, fg = fgcolour)
saveGraphButton.grid(column=5,row=12, sticky=tk.E)

if __name__ == '__race__':
    cProfile.run('race()')

app.mainloop()
