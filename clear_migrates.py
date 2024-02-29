# Press the green button in the gutter to run the script.
import os

if __name__ == '__main__':
    my_dir_list = os.listdir()
    my_dir_list.sort()
    print(f'Обнаружено объектов: {len(my_dir_list)}')
    work_dir = os.getcwd()

    for item_folder in my_dir_list:
        if os.path.isdir(item_folder) and item_folder[0] != ".":
            # --спускаемся в директорию--------------------------------------------------------------------^
            dir_path = os.path.join(os.getcwd(), item_folder)  # сюда передаем название директории
            os.chdir(dir_path)
            print(f'Анализируем директорию < {item_folder} >')

            print(f'Мы здесь {os.getcwd()}')

            inside_dir_list = os.listdir()
            inside_dir_list.sort()
            print(f'Файлов в директории: {len(inside_dir_list)}')
            print()


            s_count = 0
            for item_obj in inside_dir_list:
                if os.path.isdir(item_obj) and item_obj == "migrations":
                    # --спускаемся в директорию--------------------------------------------------------------------^
                    low_deep_dir_path = os.path.join(os.getcwd(), item_obj)  # сюда передаем название директории
                    os.chdir(low_deep_dir_path)

                    print(f'Мы здесь {os.getcwd()}')

                    in_in_side_dir_list = os.listdir()
                    for item_ in in_in_side_dir_list:
                        if item_ != "__init__.py" and not os.path.isdir(item_):
                            try:
                                os.remove(item_)

                            except Exception as e:
                                print(str(e))

                    os.chdir(dir_path)
                    print(f'Мы здесь {os.getcwd()}')

            os.chdir(work_dir)
            print(f'Мы здесь {os.getcwd()}')