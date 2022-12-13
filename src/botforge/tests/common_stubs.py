from xml.etree import ElementTree


def get_screen_view():
    screen_text = '''
    <screen id="test_screen">
        {test_title}
        
        <for item="i" from="range" delimiter="\n">
            <b>[% i %]</b> - local variables
        </for>
        
        <i>[% :range %]</i> - global variables
        
        <a href="url">Link content</a> - links
    </screen>
    '''

    xml_parser = ElementTree.XMLParser()
    xml_parser.feed(screen_text)
    tree_root = xml_parser.close()

    return {
        'filename': 'test_filename',
        'content': tree_root,
        'id': 'test_screen'
    }


def get_markup_view():
    # TODO: cover more cases with the template
    markup_text = '''
    <markup id="test_markup" one_time_keyboard="true" selective="true" resize_keyboard="true">
        <row collection="row">
            <button id="btn_row"/>
        </row>
        
        <column collection="column">
            <button id="btn_column"/>
        </column>
        
        <row>
            <button id="btn_row_x1"/>
            <button id="btn_row_x2"/>
            <button id="btn_row_x3"/>
        </row>
        
        <column>
            <button id="btn_column_x1"/>
            <button id="btn_column_x2"/>
            <button id="btn_column_x3"/>
        </column>
    </markup>
    '''

    xml_parser = ElementTree.XMLParser()
    xml_parser.feed(markup_text)
    tree_root = xml_parser.close()

    return {
        'filename': 'test_filename',
        'content': tree_root,
        'id': 'test_markup'
    }


def get_inline_markup_view():
    # TODO: cover more cases with the template
    markup_text = '''
    <inline-markup id="test_inline_markup">
        <row collection="row">
            <button id="btn_row"/>
        </row>
        
        <column collection="column">
            <button id="btn_column"/>
        </column>
        
        <row>
            <button id="btn_row_x1"/>
            <button id="btn_row_x2"/>
            <button id="btn_row_x3"/>
        </row>
        
        <column>
            <button id="btn_column_x1"/>
            <button id="btn_column_x2"/>
            <button id="btn_column_x3"/>
        </column>
    </inline-markup>
    '''

    xml_parser = ElementTree.XMLParser()
    xml_parser.feed(markup_text)
    tree_root = xml_parser.close()

    return {
        'filename': 'test_filename',
        'content': tree_root,
        'id': 'test_inline_markup'
    }


def get_form_view():
    form_text = '''
    <form id="test_form">
        <message>
            <screen id="test_screen" />
            <markup id="test_markup"/>
        </message>
    </form>
    '''

    xml_parser = ElementTree.XMLParser()
    xml_parser.feed(form_text)
    tree_root = xml_parser.close()

    return {
        'filename': 'test_filename',
        'content': tree_root,
        'id': 'test_form'
    }


def get_translator_func():
    return lambda key, **kwargs: ('[TRANSLATED]: %s; [%s] => [%s]' % (key, '|'.join(kwargs.keys()), '|'.join(kwargs.values())))


