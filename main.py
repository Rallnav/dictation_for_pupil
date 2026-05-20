import argparse
from services import GroupService, AudioService


def main():
    parser = argparse.ArgumentParser(description='听写软件')
    parser.add_argument('-c', '--config', default='config.json', help='配置文件路径')
    parser.add_argument('-g', '--group', nargs='+', help='指定听写组别，可指定多个')
    parser.add_argument('-i', '--interval', type=int, help='听写间隔（秒）')
    parser.add_argument('-r', '--repeat', type=int, help='听写次数')
    parser.add_argument('--list', action='store_true', help='列出所有组别')
    parser.add_argument('--add-group', nargs=3, metavar=('ID', 'NAME', 'CONTENT'), help='添加新组别')
    parser.add_argument('--delete-group', metavar='ID', help='删除组别')
    parser.add_argument('--set-groups', nargs='+', metavar='GROUP_ID', help='设置要听写的组别列表')
    parser.add_argument('--no-shuffle', action='store_true', help='不随机打乱听写顺序')
    parser.add_argument('--preload-all', action='store_true', help='预生成所有配置文件中的音频')
    parser.add_argument('--start-api', action='store_true', help='启动API服务')

    args = parser.parse_args()

    try:
        group_service = GroupService(args.config)
        audio_service = AudioService(args.config)

        if args.start_api:
            print('启动API服务...')
            from services import ApiService
            api_service = ApiService(args.config)
            api_service.start(host='0.0.0.0', port=8000)
            import time
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                api_service.stop()
            return

        if args.list:
            print('可用组别：')
            selected_groups = group_service.get_selected_groups()
            for group_id, group_info in group_service.get_groups().items():
                selected_mark = ' (已选)' if group_id in selected_groups else ''
                print(f"  {group_id}: {group_info['name']}{selected_mark} - {len(group_info['content'])} 个词")
            return

        if args.add_group:
            group_id, name, content_str = args.add_group
            content = [item.strip() for item in content_str.split(',')]
            new_id = group_service.add_group(group_id, name, content)
            print(f'已添加组别 {new_id}')
            return

        if args.delete_group:
            group_service.delete_group(args.delete_group)
            print(f'已删除组别 {args.delete_group}')
            return

        if args.set_groups:
            group_service.set_selected_groups(args.set_groups)
            print(f'已设置听写组别：{", ".join(args.set_groups)}')
            return

        if args.preload_all:
            print('预生成所有音频...')
            all_content = []
            for group_info in group_service.get_groups().values():
                all_content.extend(group_info['content'])
            audio_service.preload_all_audio(all_content)
            return

        groups = args.group if args.group else group_service.get_selected_groups()
        if not groups:
            print('请指定组别或在配置文件中设置 selected_groups')
            return

        interval = args.interval if args.interval else group_service.get_interval()
        repeat_count = args.repeat if args.repeat else group_service.get_repeat_count()
        long_word_extension = group_service.get_long_word_extension()

        if len(groups) == 1:
            group_id = groups[0]
            group_info = group_service.get_group(group_id)
            content = group_info['content']
            print(f'\n开始听写：{group_info["name"]}')
            print(f'组别：{group_id} | 间隔：{interval}秒 | 次数：{repeat_count}')
            print('-' * 40)
            audio_service.dictate(content, interval, repeat_count, not args.no_shuffle, long_word_extension)
        else:
            all_content = []
            for group_id in groups:
                group_info = group_service.get_group(group_id)
                for text in group_info['content']:
                    all_content.append((text, group_id, group_info['name']))
            
            print(f'\n开始听写：{len(groups)} 个组别混合')
            print(f'组别：{", ".join(groups)} | 间隔：{interval}秒 | 次数：{repeat_count}')
            print(f'总词汇数：{len(all_content)}')
            print('-' * 40)
            
            # 混合听写
            import random
            content_list = [item[0] for item in all_content]
            audio_service.dictate(content_list, interval, repeat_count, not args.no_shuffle, long_word_extension)

    except Exception as e:
        print(f'错误：{e}')


if __name__ == '__main__':
    main()
