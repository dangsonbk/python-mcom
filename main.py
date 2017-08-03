#!/usr/bin/python

import os
import sys, getopt
import xml.etree.ElementTree as XMLParser
import re
import logging

REMOVE_LIST =   ["<TabOrder>", "<TabV />", "<TabH />", "</TabOrder>", \
                    "<NormalURL \>", "<FocusURL />",\
                    "<InputWidgetMapping>", "<UserInput />", "<WidgetCallback />", "</InputWidgetMapping>", \
                    "<OnFocusCallback />", \
                    "<Value>", "<Encoding />", "<Text></Text>", "</Value>", \
                    "<Name></Name>","<Size></Size>","<Decoration></Decoration>","<TextAlign></TextAlign>","<Color></Color>","<TextDirection />",\
                    "<Name />","<Size />","<Decoration />","<TextAlign />","<Color />",\
                    "</Alpha>", "</ZOrder>", \
                    "<EventCallbackMapping>","<WidgetEvent />","<Callback />","</EventCallbackMapping>","<Key />", \
                    "<TextDirection></TextDirection>", "<TextWrap></TextWrap>", "<TextDirection>0</TextDirection>", \
                    \
                    # Some comments are not necessary
                    "ButtonWidget>", \
                    "<Location>", "</Location>", \
                    "<Size>\n", "</Size>\n", \
                    "</FocusFont>", \
                    "<Decoration>0</Decoration>", "<TextAlign>AlignLeft</TextAlign>", \
                    "<!-- Refer to sourceType string in strings.xml -->", \
                    "/bg_main.png", \
                ]

PREVENT_REMOVE = ["\<Size\>\d+\<\/Size\>"]

TRIM_SPACE_LINE = ["\<Location[X|Y]\>\d+\<\/Location[X|Y]\>", "\<Size[W|H]\>\d+\<\/Size[W|H]\>"]

def hasString(line, filterList):
    for string in filterList:
        if string in line:
            return True
    return False

def doNotRemove(line):
    for string in PREVENT_REMOVE:
        regex = re.search(string, line)
        if regex:
            return True
    return False

def trimSpaces(line):
    for string in TRIM_SPACE_LINE:
        regex = re.search(string, line)
        if regex:
            return line[4:]
    return line

def main(argv):
    input_file_filter = ""

    if argv:
        input_file_filter = argv[0]
    path_in = "../../App/Assets/GMXMLs/"
    path_in_dcv = "../../App/Assets/DCVXMLs/"
    path_out = "../../App/Assets/Xml"
    path_xml_widgetMapping = "./widgetMapping.xml"
    path_xml_signalMapping = "./signalMapping.xml"
    path_xml_alternativeWidget = "./alternativeWidget.xml"
    removed_element_count = 0
    input_size = 0
    output_size = 0
    idList = []
    skip_output = False
    skip_output_element = False
    file_count = 0

    signalMapping = {}
    widgetDictionary = []
    widgetDictionaryElement = {}
    alternativeDictionary = {}

    xmlData_widgetMapping = XMLParser.parse(path_xml_widgetMapping).getroot()
    xmlData_signalMapping = XMLParser.parse(path_xml_signalMapping).getroot()
    xmlData_alternativeWidget = XMLParser.parse(path_xml_alternativeWidget).getroot()

    for xmlScreen in xmlData_alternativeWidget:
        alternativeDictionary[xmlScreen.tag] = {}
        for xmlID in xmlScreen:
		    alternativeDictionary[xmlScreen.tag][xmlID.tag] = {}
                    for tag in xmlID:
                        alternativeDictionary[xmlScreen.tag][xmlID.tag][tag.tag] = tag.text
    for xmlScreen in xmlData_signalMapping:
        signalMapping[xmlScreen.tag] = {}

        for xmlID in xmlScreen:
            if not signalMapping[xmlScreen.tag].has_key(xmlID.tag):
                signalMapping[xmlScreen.tag][xmlID.tag] = {}
            signalMapping[xmlScreen.tag][xmlID.tag][xmlID.attrib["event"]] = xmlID.text

    for xmlWidget in xmlData_widgetMapping:
        widgetDictionaryElement = {}
        widgetDictionaryElement["ID"] = xmlWidget.tag
        widgetDictionaryElement["screen"] = xmlWidget.attrib["screen"]
        for xmlWidgetChild in xmlWidget:
            if xmlWidgetChild.tag == "startTag":
                widgetDictionaryElement["startTag"] = xmlWidgetChild.text
            elif xmlWidgetChild.tag == "closeTag":
                widgetDictionaryElement["closeTag"] = xmlWidgetChild.text
            elif xmlWidgetChild.tag == "property":
                for xmlWidgetChildChild in xmlWidgetChild:
                    if xmlWidgetChildChild.tag == "loadWidget":
                        widgetDictionaryElement["loadWidget"] = xmlWidgetChildChild.text
                    elif xmlWidgetChildChild.tag == "delegate":
                        widgetDictionaryElement["delegate"] = xmlWidgetChildChild.text
                    elif xmlWidgetChildChild.tag == "propertiesMap":
                        for xmlWidgetChildChildChild in xmlWidgetChildChild:
                            if "propertiesMap" in widgetDictionaryElement:
                                widgetDictionaryElement["propertiesMap"] += "            <" + xmlWidgetChildChildChild.tag + ">" + xmlWidgetChildChildChild.text + "</" + xmlWidgetChildChildChild.tag + ">\n"
                            else:
                                widgetDictionaryElement["propertiesMap"] = "            <" + xmlWidgetChildChildChild.tag + ">" + xmlWidgetChildChildChild.text + "</" + xmlWidgetChildChildChild.tag + ">\n"

        widgetDictionary.append(widgetDictionaryElement.copy())

    # for i in widgetDictionary:
    #     print i
    # for signals in signalMapping:
    #     print "------------------"
    #     print signalMapping[signals]

    files = [os.path.join(path_in, f) for f in os.listdir(path_in) if os.path.isfile(os.path.join(path_in, f))]
    files_dcv = [os.path.join(path_in_dcv, f) for f in os.listdir(path_in_dcv) if os.path.isfile(os.path.join(path_in_dcv, f))]
    for f in files_dcv:
        files.append(f)

    for f in files:
        if input_file_filter != "":
            regex = re.match(input_file_filter, os.path.basename(f))
            if not regex:
                continue

        skip_output = False

        idList = []
        file_count += 1

        file_name = os.path.basename(f)
        input_size += os.path.getsize(f)

        f_corrected = file_name
        if ("mutiple") in file_name:
            f_corrected = file_name.replace("mutiple", "multiple")
            print("File name corrected!: %s to %s" % (file_name, f_corrected))
        output_file = open(os.path.join(path_out, f_corrected), 'w')
        file = open(f, "r").readlines()
        currentScreen = ""
        hasSpecialEvent = False
        onDrawingWiget = ""
        preTag = ""
        for num, line in enumerate(file, 1):
            if os.path.splitext(file_name)[0] in alternativeDictionary:
                screen = alternativeDictionary[os.path.splitext(file_name)[0]]
                for item in screen:
                    if (int(screen[item]["StartLine"]) <= num and num <= int(screen[item]["EndLine"]) and screen[item]["Widget"] == "Remove"):
                        line = ""
                        continue
                    if num == int(screen[item]["StartLine"]):
                        output_file.write("    <DCVWidget>\n")
                        output_file.write("        <NormalURL>" + screen[item]["Widget"] + "</NormalURL>\n        <propertiesMap>\n")
                        output_file.write("        <objectName>" + screen[item]["ID"] + "</objectName>\n")
                        line = ""
                    if num == int(screen[item]["EndLine"]):
                        output_file.write("        </propertiesMap>\n    </DCVWidget>\n")
                        line = ""
                    if (int(screen[item]["StartLine"]) < num and num < int(screen[item]["EndLine"])):
                        if "ID" in line:
                            output_file.write(line.replace("ID", "id"))
                            line = ""
                        if "LocationX" in line:
                            output_file.write(line.replace("LocationX", "x"))
                            line = ""
                        if "LocationY" in line:
                            output_file.write(line.replace("LocationY", "y"))
                            line = ""
                        if "SizeW" in line:
                            output_file.write(line.replace("SizeW", "width"))
                            line = ""
                        if "SizeH" in line:
                            output_file.write(line.replace("SizeH", "height"))
                            line = ""

            hasSpecialEvent = False

            if ("mutiple") in line:
                line = line.replace("mutiple", "multiple")
            regex = re.search("\<ScreenID\>(\w+)\<\/ScreenID\>", line)
            if regex:
                currentScreen = regex.group(1)

            regex = re.search("\<\!--", line)
            if regex:
                onAddingTag = False
                for widgetDictionaryChild in widgetDictionary:
                    if widgetDictionaryChild["screen"] == currentScreen or widgetDictionaryChild["screen"] == "all":
                        regex_ = re.search(widgetDictionaryChild["startTag"], line)
                        # print widgetDictionaryChild["startTag"]
                        if regex_ and not onAddingTag:
                            skip_output = True
                            onAddingTag = True
                            onDrawingWiget = widgetDictionaryChild["ID"]
                            if widgetDictionaryChild["ID"] != "REMOVED":
                                # output_file.write(line)
                                output_file.write("    <DCVWidget>\n")
                                output_file.write("        <ID>" + widgetDictionaryChild["ID"] + "</ID>\n")
                                if widgetDictionaryChild["loadWidget"]:
                                    output_file.write("        <NormalURL>" + widgetDictionaryChild["loadWidget"] + "</NormalURL>\n")
                                if "delegate" in widgetDictionaryChild:
                                    if widgetDictionaryChild["delegate"]:
                                        output_file.write("        <Delegate>" + widgetDictionaryChild["delegate"] + "</Delegate>\n")
                                if "propertiesMap" in widgetDictionaryChild:
                                    if widgetDictionaryChild["propertiesMap"]:
                                        output_file.write("        <propertiesMap>\n")
                                        output_file.write(widgetDictionaryChild["propertiesMap"])
                                        output_file.write("        </propertiesMap>\n")
                        regex_ = re.search(widgetDictionaryChild["closeTag"], line)
                        if regex_ and onDrawingWiget == widgetDictionaryChild["ID"]:
                            skip_output = False
                            onAddingTag = False
                            if widgetDictionaryChild["ID"] != "REMOVED":
                                output_file.write("    </DCVWidget>\n")
                            line = ""

            line = line.replace("GMSansUI_Condensed_Global", "GM Sans UI Global Condensed")
            line = line.replace("GMSansUI_Light", "GM Sans UI Light")
            line = line.replace("GMSansUI_Medium", "GM Sans UI Medium")
            line = line.replace("GMSansUI_Regular", "GM Sans UI")

            regex = re.search("", line)

            if "<FocusFont>" in line:
                skip_output_element = True

            if "</FocusFont>" in line:
                skip_output_element = False

            if "<ListWidget>" in line:
                skip_output = True

            if "</ListWidget>" in line:
                skip_output = False
                line = ""

            # Fix duplicate id
            regex = re.search("\<ID\>(\w+)\<\/ID\>", line)
            if regex:
                if not regex.group(1) in idList:
                    idList.append(regex.group(1))
                    elementId = regex.group(1)
                else:
                    for i in range(1, 20):
                        if not regex.group(1) + "_" + str(i) in idList:
                            idList.append(regex.group(1) + "_" + str(i))
                            elementId = regex.group(1) + "_" + str(i)
                            break
                line = "        <ID>" + elementId + "</ID>" + "\n"

            # mapping event
                event = ""
                for signalMappingScreen in signalMapping:
                    if signalMappingScreen == currentScreen:
                        for signalEvent in signalMapping[signalMappingScreen]:
                            if signalEvent == elementId:
                                for key in signalMapping[signalMappingScreen][signalEvent].keys():
                                    event += "        <" + key + ">" + signalMapping[signalMappingScreen][signalEvent][key] + "</" + key + ">\n"
                                    hasSpecialEvent = True

                    if signalMappingScreen == "common" and hasSpecialEvent == False:
                        for signalEvent in signalMapping[signalMappingScreen]:
                            if signalEvent == elementId:
                                for key in signalMapping[signalMappingScreen][signalEvent].keys():
                                    event += "        <" + key + ">" + signalMapping[signalMappingScreen][signalEvent][key] + "</" + key + ">\n"

                line += event
            # Convert color
            regex = re.search("\<Color\>(\d+), ?(\d+), ?(\d+) ?\<\/Color\>", line)
            if regex:
                hexColor = "#%02x%02x%02x" % (int(regex.group(1)), int(regex.group(2)), int(regex.group(3)))
                line = "            <Color>" + hexColor + "</Color>\n"

            # Text align
            regex = re.search("\<TextAlign\>(\d+)\<\/TextAlign\>", line)
            if regex:
                if regex.group(1) == "0":
                    line = "            <TextAlign>AlignLeft</TextAlign>\n"
                elif regex.group(1) == "1":
                    line = "            <TextAlign>AlignRight</TextAlign>\n"
                elif regex.group(1) == "2":
                    line = "            <TextAlign>AlignHCenter</TextAlign>\n"

            if not skip_output:
                if not skip_output_element:
                    if not hasString(line, REMOVE_LIST):
                        output_file.write(trimSpaces(line))
                    elif doNotRemove(line):
                        output_file.write(trimSpaces(line))
                    else:
                        removed_element_count += 1

        output_file.close()
        output_size += os.path.getsize(os.path.join(path_out, f_corrected))
    if input_size!=0:
        print "----------------------------------------------------------"
        print "File processed: ", file_count
        print "Total element removed:   ", removed_element_count, "equal ", float(input_size - output_size), "Bytes"
        print "Total input files size:  ", float(input_size), "Bytes"
        print "Total output files size: ", float(output_size), "Bytes"
        print "Compress:", round((float(input_size - output_size)/float(input_size))*100, 2), "%"
    else:
        print "No file match!"
    # raw_input()
if __name__ == '__main__':
    main(sys.argv[1:])
