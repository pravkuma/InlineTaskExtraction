#!/usr/bin/env python
# coding: utf-8
import spacy
from spacy import displacy

'''
This class address all the task extraction related issues. It is using english grammar and dependency information for the 
extraction purpose.
'''
class TaskExtractor:
    # Initializations
    # This is done here so that all the required and reusable data is available any time in the memory. Loading of this class
    # and imports takes approximately 700-800MB space in the memory and is persistent throughout the session.
    # 
    # en_core_web_md is a pre-trained model that can be downloaded by running `python -m spacy download en_core_web_md` command.
    nlp = spacy.load("en_core_web_md")

    # This is limited action verb list, for better performance, more verbs needs to be included
    ACTION_VERBS = ["handle", "assign", "look", "need", "organize", "organise", "do", "get", "complete", "schedule", "find"]

    # Action verb filtering, more rules for the filter can be applied here
    def _getVerbs(self, tokens):
        verbs = []
        for token in tokens:
            if (token.lemma_ in self.ACTION_VERBS and token.pos_ == "VERB" and token.dep_ != "xcomp"):
                verbs.append(token)
                
        return verbs

    # There might be cases when the noun is not just single noun but also associated with for words like "John Doe". This needs to be
    # interpreted together also
    def _getNounChunk(self, token, noun_chunks):
        for noun_chunk in noun_chunks:
            if token in noun_chunk:
                return {"location":noun_chunk.start_char, "length":len(noun_chunk.text), "content":noun_chunk.text}
        
        # Default case, if the noun is single and not a chunk
        return {"location":token.idx, "length":len(token.text), "content":token.text}

    def _getTitleFromPreposition(self, token, noun_chunks, verb):
        # Here we need to add more to this list, "to" is just for testing. Such preposition needs to be exempted since in most of the 
        # cases they are generally used for assignment or referencing to others. This require further analysis of several preposition 
        # and then get a list of valid preposition.
        if (token.lemma_ == "to"):
            return None
        
        for child in token.children:
            if (child.dep_ == "pobj" and child.ent_type_ != 'DATE' and child.ent_type_ != 'TIME'):
                res = [
                    {"location": verb.idx, "length": len(verb.text), "content": verb.text},
                    {"location": token.idx, "length": len(token.text), "content": token.text},
                    self._getNounChunk(child, noun_chunks)
                ]
                return res
            
        return None

    def _getTitleFromXComp(self, token, noun_chunks):
        for child in token.children:
            if child.dep_ == "dobj" and child.ent_type_ != 'DATE' and child.ent_type_ != 'TIME':
                title = [
                    {"location": token.idx, "length": len(token.text), "content": token.text},
                    self._getNounChunk(child, noun_chunks)
                ]
                return title

            elif child.dep_ == "prep":
                title = self._getTitleFromPreposition(child, noun_chunks, token)
                if (title != None):
                    return title

    def _getDates(self, token):
        dates = []
        
        if token.ent_type_ == "DATE" or token.ent_type_ == "TIME":
            dates.append({"location": token.idx, "length": len(token.text), "content": token.text})
        elif token.pos_ == "PROPN" or token.pos_ =="NOUN" or token.pos_ == "PRP":
            return
        else:
            for child in token.children:
                dates += self._getDates(child)
            
        return dates

    def _getTaskWithVerb(self, verb, task, noun_chunks):
        for child in verb.children:

            #Get assignee from subtree
            if child.text.startswith("@"): 
                task['assignee'].append({"location":child.idx, "length":len(child.text), "content":child.text})

            elif child.ent_type_ == "PERSON":
                task['assignee'].append(self._getNounChunk(child, noun_chunks))
                
            elif child.dep_ == "nsubj" and child.pos_ == "PROPN":
                task['assignee'].append(self._getNounChunk(child, noun_chunks))
            
            
            #Get task title from subtree
            elif child.dep_ == "dobj" and child.ent_type_ != 'DATE' and child.ent_type_ != 'TIME':
                title = [{"location": verb.idx, "length": len(verb.text), "content": verb.text}, self._getNounChunk(child, noun_chunks)]
                task['title'].append(title)

            elif child.dep_ == "prep":
                title = self._getTitleFromPreposition(child, noun_chunks, verb)
                if (title != None):
                    task['title'].append(title)

            elif child.dep_ == "xcomp" and child.pos_ == "VERB":
                title = self._getTitleFromXComp(child, noun_chunks)
                if (title != None):
                    task['title'].append(title)
              
            
            #Get dates
            dates = self._getDates(child)
            if dates:
                task['date'] = dates

    # This function needs to be invoked for extraction purpose
    def getTask(self, text="", debug=False):
        tasks = []
        
        doc = self.nlp(text)
        sentences = list(doc.sents)

        if (debug == True):
            displacy.render(doc, style="dep", jupyter=True)
            displacy.render(doc, style="ent", jupyter=True)
        
        for sentence in sentences:
            verbs = self._getVerbs(sentence)
        
            noun_chunks = set(sentence.noun_chunks)
        
            for verb in verbs:
                sentence_phrase = {"location": sentence.start_char, "length": len(sentence.text), "content":sentence.text}
                task = {"sentence": sentence_phrase, "assignee": [], "date": [], "verb": verb.text, "title": []}
                
                self._getTaskWithVerb(verb, task, noun_chunks)  
                
                tasks.append(task)
                
        return tasks

    def test(self):
        self.getTask("@ankesh is assigned so @john needs to handle tomorrow's meeting.")

        texts = [
            "John handle tomorrow's meeting",
            "Ankesh will be looking at the computation task",
            "Complete classification job by sunday",
            "NLP task is assigned to Ankesh",
            "Ankesh is assigned with the NLP task",
            "John look at the guest coming tomorrow",
            "John handle the clients",
            "Ankesh is looking at classification task",
            "Look at the window"
        ]

        for text in texts:
            print (text)
            tasks = self.getTask(text)
            print(tasks)
            print()

            #TODO: Write asserts

def main():
    print("GenericSpacy imported")

if __name__ == "__main__":
    main()
