# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 10:06:27 2012

@author: Shreejoy
"""

import re

import neuroelectro.models as m
import resolve_data_float

from django.db.models import Count
from bs4 import BeautifulSoup
from fuzzywuzzy import process
import string

MIN_NEURON_MENTIONS_AUTO = 5

def printHtmlTable(tableTag):
    soup = BeautifulSoup(''.join(tableTag))
    tableStr = u''
    try: 
        # print title
        #title = dt.article.title
        #tableStr += title + u'\n'
        # print 'Title: ' + title.encode('utf-8')
        
        table = soup.find('table')
        captionTag = soup.find('div', {'class':'table-caption'})
        if captionTag is None:
            captionTag = soup.find('div', {'class':'auto-clean'})
        if captionTag is not None:
            caption = findTextInTag(captionTag)
    #        caption = ''.join(captionTag.findAll(text=True))
            tableStr += caption + u'\n'
        rows = table.findAll('tr')
        for tr in rows:
            headers = tr.findAll('th')
            for th in headers:
                currText = findTextInTag(th)
    #            currText = ''.join(th.findAll(text=True))
    #            if currText is None: 
    #                currText = '\t'
                text = u''.join(currText)
                tableStr += text +"|"
            cols = tr.findAll('td')
            for td in cols:
                currText = findTextInTag(td)
    #            currText = ''.join(td.findAll(text=True))
    #            if currText is None: 
    #                currText = '\t'
                text = u''.join(currText)
                tableStr += text +"|"
            tableStr += u'\n'
        footnotesTag = soup.find('div', {'class':'table-foot'})
        footnotes = findTextInTag(footnotesTag)
        tableStr += footnotes

        print tableStr.encode("iso-8859-15", "replace")
        return tableStr
    except (UnicodeDecodeError, UnicodeEncodeError):
        print 'Unicode printing failed!'
        return 

def findTextInTag(tag):
#    print tag  
#    print type(tag)
#    if tag is list:
#        tag  = tag[0]
    if tag is None:
        return u''
    textInTag = u''.join(tag.findAll(text=True))
    if textInTag is '':
        textInTag = u'    '
    textInTag = textInTag.replace('\n', u' ')
    #print textInTag
    return textInTag
# process dataTables

def unicodeToIso(inStr):
    return inStr.encode("iso-8859-15", "replace")

def getTableHeaders(tableTag):
    soup = BeautifulSoup(''.join(tableTag))
    rowHeaders = []
    columnHeaders = []
    table = soup.find('table')
    if table == None:
        return rowHeaders, columnHeaders
    rows = table.findAll('tr')
    for tr in rows:
        headers = tr.findAll('th')
        for th in headers:
            currText = findTextInTag(th)
            captionTag = th.find('div', {'class':'table-caption'})
    #            currText = ''.join(th.findAll(text=True))
    #            if currText is None: 
    #                currText = '\t'
            columnHeaders.append(currText)
        cols = tr.findAll('td')
        if len(cols)>0:
            currText = findTextInTag(cols[0])
            rowHeaders.append(currText)
    return rowHeaders, columnHeaders
    
def getTableData(tableTag):
    soup = BeautifulSoup(''.join(tableTag))
    
    table = soup.find('table')
    rows = table.findAll('tr')
    ncols = len(rows[-1].findAll('td'))
#    print 'numRows = %d numCols = %d' % (len(rows), ncols)
    dataTable = [ [ 0 for i in range(ncols) ] for j in range(len(rows) ) ]
    idTable = [ [ 0 for i in range(ncols) ] for j in range(len(rows) ) ]
#    print dataTable
#    datarunTable = [ [ '' for i in range(20) ] for j in range(20 ) ]
    rowCnt = 0
    numHeaderRows = 0
    for tr in rows:
        headers = tr.findAll('th')
        if len(headers)> 0:
            numHeaderRows += 1
        colCnt = 0
        for th in headers:
            # set colCnt by finding first non-zero element in table
            try:
                colCnt = dataTable[rowCnt].index(0)
            except ValueError:
                print 'Table is likely fucked up!!!'
                dataTable = None
                idTable = None
                return dataTable, 0, idTable
                
            currText = findTextInTag(th)
            colspan = int(th['colspan'])
            rowspan = int(th['rowspan'])
            # print currText.encode("iso-8859-15", "replace"), rowspan, colspan
            
            for i in range(rowCnt, rowCnt+rowspan):
                for j in range(colCnt, colCnt+colspan):
                    try:
                        dataTable[i][j] = currText
                        idTable[i][j] = th['id']
                    except (IndexError):
                        continue
#            if rowspan > 1:
#                print 'UH OH rowspan > 1!!'
#            insertHeaders = [ [ currText for i in range(colspan) ] for j in range(rowspan)]
#            print insertHeaders
##            currText = ''.join(th.findAll(text=True))
##            if currText is None: 
##                currText = '\t'
##            print 'row Ind = %d colInd = %d'% (rowCnt, colCnt)
##            dataTable[rowCnt][colCnt] = currText
#            dataTable[rowCnt:(rowCnt+rowspan)][colCnt:(colCnt+colspan)] = insertHeaders
#            if colspan > 1:
#                dataTable[rowCnt][colCnt:(colCnt+colspan)] = itertools.repeat(currText,colspan)
            colCnt += colspan
        cols = tr.findAll('td')
        try:
            for td in cols:
                #print rowCnt, colCnt-1
                currText = findTextInTag(td)
                dataTable[rowCnt][colCnt] = currText
                idTable[rowCnt][colCnt] = td['id']
                colCnt += 1
        except IndexError:
            print 'Table is likely fucked up!!!'
            return dataTable, 0, idTable            
            
        rowCnt += 1
        #print dataTable
    return dataTable, numHeaderRows, idTable
    
def resolveDataFloat(inStr):
    return resolve_data_float.resolve_data_float(inStr)
    
def getDigits(inStr):
    return resolve_data_float.get_digits(inStr)

def digitPct(inStr):
    return resolve_data_float.digit_pct(inStr)

def parensResolver(inStr):
    parensCheck = re.findall(u'\(.+\)', inStr)
    insideParens = None
    if len(parensCheck) > 0:
        insideParens = parensCheck[0].strip('()')
    newStr = re.sub(u'\(.+\)', '', inStr)
    return newStr, insideParens
    
def commaResolver(inStr):
    commaCheck = inStr.split(',')
    newStr = commaCheck[0]
    rightStr = None
    if len(commaCheck) > 1:
        rightStr = commaCheck[1]
    return newStr, rightStr

count = lambda l1, l2: len(list(filter(lambda c: c in l2, l1)))
def isHeader(inStr):
    num_chars = count(inStr, string.ascii_letters)
    if num_chars > 0:
        return True
    else:
        return False
    
def resolveHeader(inStr):
    newStr, insideParens = parensResolver(inStr)
    newStr, commaStr = commaResolver(newStr)
    newStr = newStr.strip()
    return newStr

ephysSyns = m.EphysPropSyn.objects.all()
ephysSynList = [e.term.lower() for e in ephysSyns]
matchThresh = 90   
 
def matchEphysHeader(headerStr):  
    h = headerStr
    normHeader = resolveHeader(h)
    if len(normHeader) == 0:
        return ''
    elif normHeader in ephysSynList: # try to match exactly
        bestMatch = normHeader
        matchVal = 100
    else: #try to fuzzy match
        processOut = process.extractOne(normHeader, ephysSynList)
        if processOut is not None:
            bestMatch, matchVal = processOut
        else:
            return ''
    if matchVal > matchThresh:
        ephysSynOb = m.EphysPropSyn.objects.get(term = bestMatch)
        ephysPropOb = ephysSynOb.ephys_prop        
        return ephysPropOb
        
def getEphysObHeaderList(headerList):
    ephysObList = []
    for h in headerList:
        ephysMatch = matchEphysHeader(h)
        if ephysMatch == '':
            ephysObList.append(None)
        else:
            ephysObList.append(ephysMatch)
    return ephysObList

# tag tables if they contain ephys props in their headers
matchThresh = 80
matchThreshShort = 95 # threshold for short terms
shortLim = 4 # number of characters for short distinction
def assocDataTableEphysVal(dataTableOb):
    dt = dataTableOb
    ds = m.DataSource.objects.get(data_table = dt)
    robot_user = m.get_robot_user()
    if dt.table_text is None:
        return
        
    tableTag = dt.table_html
    soup = BeautifulSoup(''.join(tableTag))
    headerTags = soup.findAll('th')
    #print headerTags
    tdTags = soup.findAll('td')
    allTags = headerTags + tdTags
    
    for tag in allTags:
        origTagText = tag.get_text()
        tagText = origTagText.strip()

        if 'id' in tag.attrs.keys():
            tag_id = str(tag['id'])
        else:
            tag_id = -1
        if len(tagText) == 0:
            continue
        if isHeader(tagText) is True:
            normHeader = resolveHeader(tagText)
            if len(normHeader) == 0:
                continue
            elif normHeader in ephysSynList: # try to match exactly
                bestMatch = normHeader
                matchVal = 100
            else: #try to fuzzy match
                try:
                    processOut = process.extractOne(normHeader, ephysSynList)
                    if processOut is not None:
                        bestMatch, matchVal = processOut
                    else:
                        continue
                except ZeroDivisionError:
                    continue
            if matchVal > matchThresh:
                ephysSynOb = m.EphysPropSyn.objects.get(term = bestMatch)
                ephysPropQuerySet = m.EphysProp.objects.filter(synonyms = ephysSynOb)
                if ephysPropQuerySet.count() > 0:
                    ephysPropOb = ephysPropQuerySet[0]        
                else:
                    continue
                # further check that if either header or syn is really short, 
                # match needs to be really fucking good
                if len(normHeader) <= shortLim or len(ephysSynOb.term) <= shortLim:
                    if matchVal < matchThreshShort:
                        continue
                 
                # create EphysConceptMap object
                save_ref_text = origTagText[0:min(len(origTagText),199)]
                #print save_ref_text.encode("iso-8859-15", "replace")
                #print ephysPropOb.name
#                print ephysSynOb.term
                #print matchVal    
                ephysConceptMapOb = m.EphysConceptMap.objects.get_or_create(ref_text = save_ref_text,
                                                                          ephys_prop = ephysPropOb,
                                                                          source = ds,
                                                                          dt_id = tag_id,
                                                                          match_quality = matchVal,
                                                                          added_by = robot_user,
                                                                          times_validated = 0)[0]                                                                          

def assocDataTableEphysValMult(dataTableObs):
    cnt = 0
    for dt in dataTableObs:
        cnt = cnt + 1
        if cnt % 100 == 0:
            print '%d of %d tables' % (cnt, dataTableObs.count())   
        assocDataTableEphysVal(dt)


def assignNeuronToTableTag(neuronOb, dataTableOb, tableTag):
    tag_id = tableTag['id']
    headerText = tableTag.text.strip()
    successBool = False
    if headerText is None:
        return successBool
    # check that there isn't already a ncm here
    if m.NeuronConceptMap.objects.filter(dt_id = tag_id, data_table = dataTableOb).exclude(added_by = 'robot').distinct().count() > 0:
        successBool = True        
        return successBool
    save_ref_text = headerText[0:min(len(headerText),199)]
    neuronConceptMapOb = m.NeuronConceptMap.objects.get_or_create(ref_text = save_ref_text,
                                                              neuron = neuronOb,
                                                              data_table = dataTableOb,
                                                              dt_id = tag_id,
                                                              added_by = 'robot')[0]    
    successBool = True        
    return successBool                                                              
# use a simple heuristic to tag data table headers for neuron concepts
def assocDataTableNeuronAuto(dataTableOb):
    soup = BeautifulSoup(dataTableOb.table_html)
    ecmObs = m.EphysConceptMap.objects.filter(data_table = dataTableOb)
    ecmTableIds = [ecmOb.dt_id for ecmOb in ecmObs]    
    namObs = m.NeuronArticleMap.objects.filter(article__datatable = dataTableOb).order_by('-num_mentions')
    if namObs[0].num_mentions < MIN_NEURON_MENTIONS_AUTO:
        return
    topNeuronOb = namObs[0].neuron
    
#    numTH = len(soup.findAll('th'))
#    numTR = len(soup.findAll('tr'))
#    numTD = len(soup.findAll('td'))
    ecmAllTD = True
    for e in ecmTableIds:
        if 'td' in e:
            continue
        else:
            ecmAllTD = False
            break
    # if all ephys entities are td, then call first nonblank header element top neuron
    successBool = False
    if ecmAllTD == True:
        headerTags = soup.findAll('th')
        if len(headerTags) >= 2:
            # assign neuron to header tag in 1th position
            firstHeaderTag = headerTags[1]            
            successBool = assignNeuronToTableTag(topNeuronOb, dataTableOb, firstHeaderTag)
            # call first nonblank header element top neuron
#             if successBool == False:
#                 firstHeaderTag = soup.findAll('th', text != None)
#                 successBool = assignNeuronToTableTag(topNeuronOb, dataTableOb, firstHeaderTag) 
    print dataTableOb.pk, successBool                                                                      
               
def assocDataTableNeuronAutoMult(dataTableObs):
    cnt = 0
    for dt in dataTableObs:
        cnt = cnt + 1
        if cnt % 100 == 0:
            print '%d of %d tables' % (cnt, dataTableObs.count())   
        assocDataTableNeuronAuto(dt)    
               
           
def countDataTableMethods():
    dts = m.DataTable.objects.annotate(num_ecms=Count('ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.order_by('-num_ecms')
    dts.filter()
                
def assignDataValsToNeuronEphys(dt, user = None):
    # check that dt has both ephys obs and neuron concept obs
    try:
        tableSoup = BeautifulSoup(dt.table_html)
        ds = m.DataSource.objects.get(data_table = dt)
        if ds.ephysconceptmap_set.all().count() > 0 and ds.neuronconceptmap_set.all().count() > 0:
            dataTable, numHeaderRows, idTable = getTableData(dt.table_html)
            if dataTable is None or idTable is None:
                return
            ecmObs = ds.ephysconceptmap_set.all()
            ncmObs = ds.neuronconceptmap_set.all()
            for n in ncmObs:
                nId = n.dt_id
                nRowInd, nColInd = getInd(nId, idTable)
                for e in ecmObs:
                    eId = e.dt_id
                    if eId =='-1' or len(idTable) == 0:
                        continue
                    eRowInd, eColInd = getInd(eId, idTable)
                    dataValRowInd = max(nRowInd, eRowInd)
                    dataValColInd = max(nColInd, eColInd)
                    dataValIdTag = idTable[dataValRowInd][dataValColInd]
                    data_tag = tableSoup.find(id = dataValIdTag)
                    if data_tag is None:
                        continue
                    ref_text = data_tag.get_text()
                    retDict = resolveDataFloat(ref_text)
                    #print retDict
                    if 'value' in retDict.keys():
                        val = retDict['value']
                        nedmOb = m.NeuronEphysDataMap.objects.get_or_create(source = ds,
                                                                 ref_text = ref_text,
                                                                 dt_id = dataValIdTag,
                                                                 #added_by = 'robot',
                                                                 neuron_concept_map = n,
                                                                 ephys_concept_map = e,
                                                                 val = val,
                                                                 times_validated = 0,
                                                                 )[0]
                        if user:
                        	nedmOb.added_by = user
                        if 'error' in retDict.keys():
                            err = retDict['error']
                            nedmOb.err = err
                        if 'numCells' in retDict.keys():
                            num_reps = retDict['numCells']    
                            nedmOb.n = num_reps
                        nedmOb.save()
    except (TypeError):
        return
                    #print nedmOb
                #print nRowInd, nColInd, eRowInd, eColInd

def assignDataValsToNeuronEphysMult(dataTableObs):
    cnt = 0
    for dt in dataTableObs:
        cnt = cnt + 1
        if cnt % 10 == 0:
            print '%d of %d tables' % (cnt, dataTableObs.count())   
        assignDataValsToNeuronEphys(dt)  

def getInd(elem, mat):
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == elem:
                return i, j                

