from xml.etree import ElementTree

node = ElementTree.fromstring('<mount -species="Jackalope"/>')
print(node.get('species'))
