-- DROP FUNCTION public.udf_spots_nearby_current_user_position(integer, double precision, double precision);
CREATE OR REPLACE FUNCTION public.udf_spots_nearby_current_user_position(
    param_user_id integer,
    param_lat double precision,
    param_lng double precision)
  RETURNS json AS
$BODY$

DECLARE

  json_returning json = '{}';
  i RECORD;
    
  BEGIN        

  /*
  -- To Test:
    SELECT udf_spots_nearby_current_user_position(23,-80.1358946,25.7697018);
  */

  -- Create a temporary table to store nearby places
  CREATE TEMPORARY TABLE IF NOT EXISTS temporal_spots_table (
        id integer,
        name character varying,
        lat double precision,
        lng double precision,
        country character varying,
        state_name character varying,
        city character varying,
        is_active boolean DEFAULT true
  );

  INSERT INTO temporal_spots_table(
    id,
    name,
    lat,
    lng,
    country,
    state_name,
    city,
    is_active
  )
  -- Get the first 5 places of the current user near where you are, using PostGIS
  SELECT
    id,
    name,
    lat,
    lng,
    country,
    state_name,
    city,
    is_active
  FROM
    spot
  WHERE
    user_id = param_user_id
    /*
    AND 
    lat != param_lat
    AND
    lng != param_lng
    */
    AND
    is_active
    AND
    NOT is_deleted
  ORDER BY 
    geom <-> ST_SetSRID(ST_MakePoint(param_lng,param_lat),4326) limit 5;

    -- Only for temporal_spots_table test purpose 
    /*
    FOR i IN (
      SELECT *
      FROM
        temporal_spots_table
      ) LOOP

      RAISE NOTICE 'spot_id: %',i.id;

    END LOOP;
    */

  IF EXISTS (
    SELECT
      id
    FROM
      temporal_spots_table
    ) THEN

      RAISE NOTICE 'Were found places near where you are';

      SELECT JSON_AGG(a.*) INTO STRICT json_returning
      FROM (
        SELECT
          tst.id "spotId",
          tst.name "spotName",
          tst.lat,
          tst.lng,
          tst.country,
          tst.city,
          tst.is_active/*,
          (
            SELECT ARRAY_AGG(b.*) "imageList"
            FROM (
              SELECT --DISTINCT ON (si.id)
                si.id "imageId",
                si.url "imageURL",
                si.extension,
                si.principalimage,
                si.is_active
              FROM image si
                INNER JOIN spot s
                  ON si.spot_id = s.id
                  AND
                  si.is_active
                  AND
                  not si.is_deleted                      
                  AND
                  s.is_active
                  AND
                  not s.is_deleted
                  AND
                  s.user_id = param_user_id
                  AND
                  s.id = tst.id
              GROUP BY
                si.id, si.spot_id
              ORDER BY 
                si.id, si.principalimage
            )b
          )*/
        FROM 
          temporal_spots_table tst     
      )a;

  ELSE

    RAISE NOTICE 'Were not found places near where you are';

    json_returning  = '[{
        "spotId": null,
        "spotName": null,
        "lat": null,
        "lng": null,
        "country": null,
        "city": null,
        "is_active": null,
      }]';

  END IF;

    RETURN json_returning;

  DROP TABLE IF EXISTS temporal_spots_table;
  --COMMIT;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.udf_spots_nearby_current_user_position(integer, double precision, double precision)
  OWNER TO postgres;