import argparse

from convert_scenario import convert_html

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tsv_file')
    parser.add_argument('html_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--year', required=True, type=int)
    args = parser.parse_args()

    with open(args.tsv_file) as scenario_list_file:
        for line in scenario_list_file:
            fields = line.strip().split('\t')
            name = fields[0]
            title = fields[1]
            url = fields[2]
            author = fields[3]
            teaser = fields[4]
            credits_data = (title, author, args.year, url)
            print(f'Converting {name}')
            html_path = f'{args.html_dir}/{name}.html'
            out_path = f'{args.output_dir}/{name}.wd'
            convert_html(html_path, out_path, credits_data=credits_data)

