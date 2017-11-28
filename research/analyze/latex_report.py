class LatexGenerator():

    def get_latex_items(items):
        head = r"\begin{itemize}"
        body = ""
        for item in items:
            body += r'\item {}'.format(item)
        tail = r'\end{itemize}'
        return head + body + tail 

    def get_latex_section(body, title):
        head = '\\section{' + title + '}\n'
        return head + body


    def get_latex_subsection(body, title):
        head = '\\subsection{' + title + '}\n'
        return head + body


    def get_latex_doc(body):
        with open('./report/base.tex', 'r') as base:
            out_lines = []
            for line in base.readlines():
                out_lines.append(line.replace('qwerbodyqwer', body))

        with open('./report/report.tex', 'w') as output:
            for line in out_lines:
                output.write(line)

        os.system("cd ./report && pdflatex -synctex=1 -interaction=nonstopmode \"report\".tex")
        
    def get_latex_pic(path):
        head = r"\begin{figure}[H]"
        head += r'\centering'
        body = r'\includegraphics[width=75mm,scale=0.5]{' + path + '}'
        #body += r'\caption{How many users changed in days}'
        tail = r'\end{figure}'
        return head + body + tail

    def get_latex_section(body, title):
        head = '\\section{' + title + '}\n'
        return head + body


    def get_latex_subsection(body, title):
        head = '\\subsection{' + title + '}\n'
        return head + body


    def get_latex_doc(body):
        with open('./report/base.tex', 'r') as base:
            out_lines = []
            for line in base.readlines():
                out_lines.append(line.replace('qwerbodyqwer', body))

        with open('./report/report.tex', 'w') as output:
            for line in out_lines:
                output.write(line)

        os.system("cd ./report && pdflatex -synctex=1 -interaction=nonstopmode \"report\".tex")
        
    def get_latex_pic(path):
        head = r"\begin{figure}[H]"
        head += r'\centering'
        body = r'\includegraphics[width=75mm,scale=0.5]{' + path + '}'
        #body += r'\caption{How many users changed in days}'
        tail = r'\end{figure}'
        return head + body + tail


