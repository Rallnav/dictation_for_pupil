import argparse
from dictation import DictationEngine
from group_manager import GroupManager


def main():
    parser = argparse.ArgumentParser(description='听写软件')
    parser.add_argument('-c', '--config', default='config.json', help='配置文件路径')
    parser.add_argument('-g', '--group', nargs='+', help='指定听写组别，可指定多个')
    parser.add_argument('-i', '--interval', type=int, help='听写间隔（秒）')
    parser.add_argument('-r', '--repeat', type=int, help='听写次数')
    parser.add_argument('--list', action='store_true', help='列出所有组别')
    parser.add_argument('--add-group', nargs=3, metavar=('ID', 'NAME', 'CONTENT'), help='添加新组别，内容用逗号分隔')
    parser.add_argument('--delete-group', metavar='ID', help='删除组别')
    parser.add_argument('--set-groups', nargs='+', metavar='GROUP_ID', help='设置要听写的组别列表')
    parser.add_argument('--no-shuffle', action='store_true', help='不随机打乱听写顺序（默认随机）')
    parser.add_argument('--preload-all', action='store_true', help='预生成所有配置文件中的音频')

    args = parser.parse_args()

    try:
        manager = GroupManager(args.config)
        engine = DictationEngine(args.config)

        if args.list:
            print('可用组别：')
            selected_groups = manager.get_selected_groups()
            for group_id, group_info in manager.get_groups().items():
                selected_mark = ' (已选)' if group_id in selected_groups else ''
                print(f"  {group_id}: {group_info['name']}{selected_mark} - {len(group_info['content'])} 个词")
            return

        if args.add_group:
            group_id, name, content_str = args.add_group
            content = [item.strip() for item in content_str.split(',')]
            manager.add_group(group_id, name, content)
            print(f'已添加组别 {group_id}')
            return

        if args.delete_group:
            manager.delete_group(args.delete_group)
            print(f'已删除组别 {args.delete_group}')
            return

        if args.set_groups:
            manager.set_selected_groups(args.set_groups)
            print(f'已设置听写组别：{", ".join(args.set_groups)}')
            return

        if args.preload_all:
            print('预生成所有音频...')
            engine.preload_all_audio(manager)
            return

        groups = args.group if args.group else manager.get_selected_groups()
        if not groups:
            print('请指定组别或在配置文件中设置 selected_groups')
            return

        interval = args.interval if args.interval else manager.get_interval()
        repeat_count = args.repeat if args.repeat else manager.get_repeat_count()

        if len(groups) == 1:
            group_id = groups[0]
            group_info = manager.get_group(group_id)
            content = group_info['content']
            print(f'\n开始听写：{group_info["name"]}')
            print(f'组别：{group_id} | 间隔：{interval}秒 | 次数：{repeat_count}')
            print('-' * 40)
            engine.dictate(content, interval, repeat_count, not args.no_shuffle)
        else:
            all_content = []
            for group_id in groups:
                group_info = manager.get_group(group_id)
                for text in group_info['content']:
                    all_content.append((text, group_id, group_info['name']))
            
            print(f'\n开始听写：{len(groups)} 个组别混合')
            print(f'组别：{", ".join(groups)} | 间隔：{interval}秒 | 次数：{repeat_count}')
            print(f'总词汇数：{len(all_content)}')
            print('-' * 40)
            engine.dictate_mixed(all_content, interval, repeat_count, not args.no_shuffle)

    except Exception as e:
        print(f'错误：{e}')


if __name__ == '__main__':
    main()
