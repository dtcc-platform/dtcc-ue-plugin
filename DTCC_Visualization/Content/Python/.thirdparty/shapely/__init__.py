

""""""# start delvewheel patch
def _delvewheel_init_patch_1_0_1():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'Shapely.libs'))
    if sys.version_info[:2] >= (3, 8) and not os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')) or sys.version_info[:2] >= (3, 10):
        os.add_dll_directory(libs_dir)
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-Shapely-1.8.5.post1')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_1_0_1()
del _delvewheel_init_patch_1_0_1
# end delvewheel patch

__version__ = "1.8.5.post1"
