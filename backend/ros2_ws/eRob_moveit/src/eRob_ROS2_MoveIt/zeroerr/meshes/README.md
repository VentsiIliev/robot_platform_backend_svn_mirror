# Shared mesh assets

Robot meshes are grouped by physical model under `robots/zeroerr`: shared links
in `common`, and alternative links in `short_links` and `extended_links`.
STL and DAE files are retained separately; their geometry is not assumed equal.

`tools` contains pointer, gripper and distinct disk geometry. `cells` contains
mounting geometry; compact-table original geometry and its transform metadata
stay together. `components` contains reusable ring geometry. Distinct meshes,
including backups and centered variants, are preserved byte for byte.

URDF/Xacro descriptions own scale and attachment transforms. Referencing one
shared mesh does not imply identical mounting offsets, joint origins or TCPs.
Do not copy robot meshes into application/profile folders.

`migration_paths.json` records previous paths relative to this directory and
canonical replacements. Exact SHA-256 matches were consolidated; filenames or
visual similarity alone were not used to discard geometry.

After pulling this migration, rebuild the `zeroerr` package in the deployed ROS
workspace before restarting the backend, so installed descriptions and meshes
are updated together. This asset migration does not change the active profile,
mounting transforms, collision geometry or configuration composition.
