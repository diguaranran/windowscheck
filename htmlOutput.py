#coding:gbk

def writeHtmlHead(hResFile):
    body  = '<html>\r\n'
    body += '<head>\r\n'
    body += '<meta http-equiv="Content-Type" content="text/html; charset=gb2312" />\r\n'
    body += '<title>窗口性能检测结果</title>\r\n'
    body += '</head>\r\n'
    body += '<body>\r\n'
    body += '<h1 align="center">窗口性能检测结果</h1>'
    hResFile.write(body)

def writeTableHead(hResFile):
    body = '<table width="80%" align="center" cellspacing="0" style="table-layout: fixed;WORD-WRAP: break-word;border-left:1px solid black;border-top:1px solid black">\r\n'
    body += '<tr align="center">'
    body += '<td rowspan="2" width="20%" style="border-right:1px solid black;border-bottom:1px solid black" nowrap><strong><font size="4">exe名称</font></strong></td>\r\n'
    body += '<td colspan="11" style="border-right:1px solid black;border-bottom:1px solid black" nowrap><strong><font size="4">窗口弹出耗时(秒)</font></strong></td>\r\n'
    body += '</tr>\r\n'
    body += '<tr align="center">'
    for i in range(1, 11):
        body += '<td style="border-right:1px solid black;border-bottom:1px solid black" nowrap><strong><font size="4">%d</font></strong></td>\r\n'%i
    body += '<td style="border-right:1px solid black;border-bottom:1px solid black" nowrap><strong><font size="4">平均值</font></strong></td>\r\n'
    body += '</tr>\r\n'
    hResFile.write(body)

def writeCheckItem(hResFile, exeName, timeList, average):
    body = '<tr align="center">'
    body += '<td style="border-right:1px solid black;border-bottom:1px solid black">%s</td>\r\n'%exeName
    for t in timeList:
        if t == -1:
            body += '<td style="border-right:1px solid black;border-bottom:1px solid black">-</td>\r\n'
        else:
            body += '<td style="border-right:1px solid black;border-bottom:1px solid black">%.4f</td>\r\n'%t
    body += '<td style="border-right:1px solid black;border-bottom:1px solid black">%.4f</td>\r\n'%average
    body += '</tr>\r\n'
    hResFile.write(body)

def writeTableTail(hResFile):
    body = '</table>\r\n'
    hResFile.write(body)

def writeHtmlTail(hResFile):
    body = '</body>\r\n'
    body += '</html>\r\n'
    hResFile.write(body)